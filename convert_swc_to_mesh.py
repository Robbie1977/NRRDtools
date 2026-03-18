#!/usr/bin/env python3
"""Convert SWC skeleton files to OBJ meshes (volume_man.obj).

For neurons that have SWC tracings, this script inflates the skeleton into
a tubular mesh and saves it as OBJ.

Two mesh-generation approaches are provided:
  1. navis-based (preferred): Uses navis.conversion.tree2meshneuron()
  2. trimesh-based (fallback): Manually creates truncated cones along each edge

Based on: https://github.com/VirtualFlyBrain/imageFileConvertion/blob/main/convert_swc_to_mesh.py
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import trimesh


# ---------------------------------------------------------------------------
# SWC parsing
# ---------------------------------------------------------------------------

def parse_swc(filepath):
    """Parse an SWC file into a dict of nodes.

    Returns:
        {node_id: {"x": float, "y": float, "z": float,
                    "radius": float, "parent": int, "type": int}}
    """
    nodes = {}
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 7:
                continue
            node_id = int(parts[0])
            try:
                radius = float(parts[5])
            except ValueError:
                radius = float("nan")
            nodes[node_id] = {
                "type": int(parts[1]),
                "x": float(parts[2]),
                "y": float(parts[3]),
                "z": float(parts[4]),
                "radius": radius,
                "parent": int(parts[6]),
            }
    return nodes


# ---------------------------------------------------------------------------
# Approach 1: navis-based conversion (preferred)
# ---------------------------------------------------------------------------

def swc_to_mesh_navis(swc_path, verbose=True):
    """Convert SWC to mesh using navis (requires navis + CGAL or scipy)."""
    try:
        import navis
    except ImportError:
        raise ImportError("navis required for this method. Install with: pip install navis")

    if verbose:
        print("  Using navis for SWC -> mesh conversion")

    neuron = navis.read_swc(swc_path)

    if verbose:
        print(f"  Loaded neuron: {neuron.n_nodes} nodes, {neuron.n_branches} branches")

    # Convert TreeNeuron to MeshNeuron
    mesh_neuron = navis.conversion.tree2meshneuron(neuron)

    if verbose:
        print(f"  Generated mesh: {len(mesh_neuron.vertices)} vertices, {len(mesh_neuron.faces)} faces")

    return trimesh.Trimesh(
        vertices=mesh_neuron.vertices,
        faces=mesh_neuron.faces,
    )


# ---------------------------------------------------------------------------
# Approach 2: trimesh-based tube generation (fallback)
# ---------------------------------------------------------------------------

def create_tube_segment(p1, p2, r1, r2, n_sides=8):
    """Create a truncated cone (tube segment) between two points."""
    direction = p2 - p1
    length = np.linalg.norm(direction)
    if length < 1e-10:
        return None

    cylinder = trimesh.creation.cylinder(
        radius=1.0, height=length, sections=n_sides
    )

    verts = cylinder.vertices.copy()
    top_mask = verts[:, 2] > 0
    bottom_mask = ~top_mask
    verts[top_mask, 0] *= r2
    verts[top_mask, 1] *= r2
    verts[bottom_mask, 0] *= r1
    verts[bottom_mask, 1] *= r1

    cylinder.vertices = verts

    direction_norm = direction / length
    z_axis = np.array([0, 0, 1.0])

    if np.allclose(direction_norm, z_axis):
        rotation = np.eye(4)
    elif np.allclose(direction_norm, -z_axis):
        rotation = trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0])
    else:
        axis = np.cross(z_axis, direction_norm)
        axis = axis / np.linalg.norm(axis)
        angle = np.arccos(np.clip(np.dot(z_axis, direction_norm), -1, 1))
        rotation = trimesh.transformations.rotation_matrix(angle, axis)

    cylinder.apply_transform(rotation)

    midpoint = (p1 + p2) / 2.0
    cylinder.apply_translation(midpoint)

    return cylinder


def swc_to_mesh_tubes(swc_path, tube_sides=20, min_radius=0.2, verbose=True):
    """Convert SWC to mesh by creating tube segments along each edge."""
    nodes = parse_swc(swc_path)

    if verbose:
        print(f"  Using tube generation: {len(nodes)} nodes, {tube_sides} sides per tube")

    meshes = []
    for node_id, node in nodes.items():
        parent_id = node["parent"]
        if parent_id < 0 or parent_id not in nodes:
            continue

        parent = nodes[parent_id]
        p1 = np.array([parent["x"], parent["y"], parent["z"]])
        p2 = np.array([node["x"], node["y"], node["z"]])
        r1 = parent["radius"] if not np.isnan(parent["radius"]) else min_radius
        r1 = max(r1, min_radius)
        r2 = node["radius"] if not np.isnan(node["radius"]) else min_radius
        r2 = max(r2, min_radius)

        tube = create_tube_segment(p1, p2, r1, r2, n_sides=tube_sides)
        if tube is not None:
            meshes.append(tube)

    # Add spheres at branch points for smoother junctions
    child_count = {}
    for node in nodes.values():
        pid = node["parent"]
        if pid > 0:
            child_count[pid] = child_count.get(pid, 0) + 1

    for nid, count in child_count.items():
        if count > 1 and nid in nodes:
            node = nodes[nid]
            r = node["radius"] if not np.isnan(node["radius"]) else min_radius
            r = max(r, min_radius)
            sphere = trimesh.creation.icosphere(subdivisions=1, radius=r)
            sphere.apply_translation([node["x"], node["y"], node["z"]])
            meshes.append(sphere)

    if not meshes:
        raise ValueError("No tube segments could be generated from SWC")

    if verbose:
        print(f"  Created {len(meshes)} tube/sphere primitives, merging...")

    combined = trimesh.util.concatenate(meshes)

    if verbose:
        print(f"  Merged mesh: {len(combined.vertices)} vertices, {len(combined.faces)} faces")

    return combined


def swc_to_obj(swc_path, obj_path, method="navis", tube_sides=20, verbose=True):
    """Convert SWC to OBJ mesh file.

    Returns the generated trimesh for inspection/further use.
    """
    if verbose:
        print(f"Converting SWC to mesh: {swc_path}")

    if method == "navis":
        try:
            mesh = swc_to_mesh_navis(swc_path, verbose=verbose)
        except ImportError:
            if verbose:
                print("  navis not available, falling back to tube method")
            mesh = swc_to_mesh_tubes(swc_path, tube_sides=tube_sides,
                                     verbose=verbose)
    else:
        mesh = swc_to_mesh_tubes(swc_path, tube_sides=tube_sides,
                                 verbose=verbose)

    mesh.export(obj_path, file_type="obj")

    if verbose:
        print(f"  Saved OBJ: {obj_path} "
              f"({len(mesh.vertices)} vertices, {len(mesh.faces)} faces)")

    # Set permissions (best effort)
    try:
        os.chmod(obj_path, 0o777)
    except Exception:
        pass

    return mesh


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Convert SWC skeleton files to OBJ meshes"
    )
    parser.add_argument("--input-swc", required=True,
                        help="Path to local SWC file")
    parser.add_argument("--output-dir", default=None,
                        help="Output directory (default: same as SWC file)")
    parser.add_argument("--method", choices=["navis", "tubes"], default="navis",
                        help="Mesh generation method (default: navis)")
    parser.add_argument("--tube-sides", type=int, default=20,
                        help="Number of sides per tube segment (tubes method, default: 20)")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    swc_path = os.path.abspath(args.input_swc)
    if not os.path.exists(swc_path):
        print(f"Error: SWC file not found: {swc_path}")
        return 1

    output_dir = args.output_dir or os.path.dirname(swc_path)
    obj_path = os.path.join(output_dir, "volume_man.obj")

    swc_to_obj(swc_path, obj_path, method=args.method,
               tube_sides=args.tube_sides, verbose=args.verbose)

    print(f"Done. OBJ at: {obj_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
