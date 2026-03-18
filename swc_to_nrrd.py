#!/usr/bin/env python3
import argparse
import glob
import os
import sys
from pathlib import Path

import numpy as np
import nrrd
import navis

from nblast_pipeline.pipeline_status import (
    EMPTY_VOXELIZATION,
    SHAPE_MISMATCH,
    SWC_OUT_OF_BOUNDS,
    SWC_PARSE_ERROR,
)


# ---------------------------------------------------------------------------
# Core conversion + status helpers
# ---------------------------------------------------------------------------

def convert_swc_to_nrrd_with_status(swc_file, template_file, output_file):
    """Convert SWC to NRRD and return structured status.

    Returns:
        dict: {
            "success": bool,
            "error_category": str|None,
            "error_detail": str|None,
            "voxel_count": int,
        }
    """

    status = {
        "success": False,
        "error_category": None,
        "error_detail": None,
        "voxel_count": 0,
    }

    try:
        template_data, template_header = nrrd.read(template_file)
    except Exception as e:
        status["error_category"] = "TEMPLATE_READ_ERROR"
        status["error_detail"] = str(e)
        return status

    try:
        neuron = navis.read_swc(swc_file)
    except Exception as e:
        status["error_category"] = SWC_PARSE_ERROR
        status["error_detail"] = str(e)
        return status

    # Get voxel size from template
    space_directions = template_header["space directions"]
    voxel_size = np.array([np.linalg.norm(d) for d in space_directions])
    origin = np.array(template_header.get("space origin", [0, 0, 0]))

    print(f"Template shape: {template_data.shape}")
    print(f"Voxel size: {voxel_size}")
    print(f"Origin: {origin}")
    print(f"Loaded neuron with {len(neuron.nodes)} nodes")
    print(f"Bounding box (microns): {neuron.bbox}")

    # Convert from microns to voxel coordinates
    # voxel = (micron - origin) / voxel_size
    neuron.nodes[["x", "y", "z"]] = (neuron.nodes[["x", "y", "z"]] - origin) / voxel_size
    print(f"Bounding box (voxels): {neuron.bbox}")

    # Detect fully out-of-bounds (all points lie outside template volume)
    # neuron.bbox is ((min, max), (min, max), (min, max))
    bbox = neuron.bbox
    dims = template_data.shape
    out_of_bounds = (
        bbox[0][1] < 0
        or bbox[1][1] < 0
        or bbox[2][1] < 0
        or bbox[0][0] >= dims[0]
        or bbox[1][0] >= dims[1]
        or bbox[2][0] >= dims[2]
    )
    if out_of_bounds:
        status["error_category"] = SWC_OUT_OF_BOUNDS
        status["error_detail"] = f"Bounding box {bbox} outside template bounds {dims}"
        return status

    # Voxelize at pitch=1 (now in voxel space)
    bounds = np.array([[0, dims[0]], [0, dims[1]], [0, dims[2]]])
    voxel_neuron = navis.voxelize(
        neuron,
        pitch=1,
        bounds=bounds,
    )

    # Get volume as numpy array
    volume = voxel_neuron.grid.astype(np.uint8)
    volume[volume > 0] = 255

    # If the volume doesn't match the template size exactly, record a mismatch.
    if volume.shape != dims:
        status["error_category"] = SHAPE_MISMATCH
        status["error_detail"] = f"Voxelization shape {volume.shape} does not match template {dims}"
        # Attempt to adjust in case downstream steps still want the file
        adjusted = np.zeros(dims, dtype=np.uint8)
        x_max = min(volume.shape[0], dims[0])
        y_max = min(volume.shape[1], dims[1])
        z_max = min(volume.shape[2], dims[2])
        adjusted[:x_max, :y_max, :z_max] = volume[:x_max, :y_max, :z_max]
        volume = adjusted

    voxel_count = int(np.count_nonzero(volume))
    status["voxel_count"] = voxel_count

    print(f"Output shape: {volume.shape}")
    print(f"Non-zero voxels: {voxel_count}")

    if voxel_count == 0:
        status["error_category"] = EMPTY_VOXELIZATION
        status["error_detail"] = "No non-zero voxels were produced (empty volume)"
        return status

    # Build output header explicitly preserving spatial metadata
    output_header = {
        "type": "uint8",
        "dimension": 3,
        "sizes": volume.shape,
        "encoding": template_header.get("encoding", "gzip"),
    }

    # Copy spatial metadata from template
    if "space" in template_header:
        output_header["space"] = template_header["space"]
    if "space directions" in template_header:
        output_header["space directions"] = template_header["space directions"]
    if "space origin" in template_header:
        output_header["space origin"] = template_header["space origin"]
    if "kinds" in template_header:
        output_header["kinds"] = template_header["kinds"]

    # Write output
    nrrd.write(output_file, volume, header=output_header)
    print(f"Saved: {output_file}")

    # Set permissions
    os.chmod(output_file, 0o777)

    # Verify the output
    _, verify_header = nrrd.read(output_file)
    print(f"Verified output header:")
    for key in ["space", "space directions", "space origin", "sizes"]:
        if key in verify_header:
            print(f"  {key}: {verify_header[key]}")

    # Success
    status["success"] = True
    # If the only issue was a shape mismatch, keep that info but report success
    return status


def convert_swc_to_nrrd(swc_file, template_file, output_file):
    """Backward compatible wrapper returning simple bool."""
    result = convert_swc_to_nrrd_with_status(swc_file, template_file, output_file)
    return result.get("success", False)


# ---------------------------------------------------------------------------
# Legacy helpers / CLI retained for compatibility
# ---------------------------------------------------------------------------

MIN_VALID_VOXELS = 100
MIN_DIMENSION = 10


def get_template_path(template_id):
    """Construct template path from VFB template ID."""
    # template_id format: VFB_00101567
    # Path format: /IMAGE_DATA/VFB/i/0010/1567/VFB_00101567/template.nrrd
    part1 = template_id[4:8]  # e.g., "0010"
    part2 = template_id[8:12]  # e.g., "1567"
    return f"/IMAGE_DATA/VFB/i/{part1}/{part2}/{template_id}/template.nrrd"


def strip_leading_whitespace(swc_path):
    """Strip leading whitespace from SWC file lines (like the sed command did)."""
    try:
        with open(swc_path, "r") as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        import gzip

        with gzip.open(swc_path, "rt") as f:
            lines = f.readlines()

    stripped = [line.lstrip() for line in lines]

    if stripped != lines:
        print(f"  Stripping leading whitespace from {swc_path}")
        with open(swc_path, "w") as f:
            f.writelines(stripped)


def is_valid_nrrd(nrrd_path, template_shape=None):
    """Check if NRRD file exists and is valid (not empty/broken)."""
    if not os.path.exists(nrrd_path):
        return False, "missing"

    if os.path.getsize(nrrd_path) == 0:
        return False, "empty file"

    try:
        data, header = nrrd.read(nrrd_path)

        # Check if dimensions are too small
        if any(d < MIN_DIMENSION for d in data.shape):
            return False, f"dimensions too small: {data.shape}"

        # Check if there's actual content
        nonzero = np.count_nonzero(data)
        if nonzero < MIN_VALID_VOXELS:
            return False, f"too few non-zero voxels: {nonzero}"

        # Check if shape matches template (if provided)
        if template_shape is not None and data.shape != template_shape:
            return False, f"shape mismatch: {data.shape} vs template {template_shape}"

        return True, "valid"

    except Exception as e:
        return False, f"error reading: {e}"


def clean_derived_files(swc_path):
    """Remove files that depend on the NRRD and need regenerating."""
    parent = Path(swc_path).parent
    patterns = [
        "thumbnail.png",
        "thumbnailT.png",
        "volume.wlz",
        "volume_bonded.wlz",
        "volume_bonded.tif",
        "volume_bounded.nrrd",
        "volume_bounded.tif",
        "volume.obj",
    ]
    for pattern in patterns:
        for old_file in parent.glob(pattern):
            print(f"  Removing: {old_file}")
            old_file.unlink()


def process_swc_file(swc_path, redo=False):
    """Process a single SWC file. Returns (swc_path, success, message)."""
    try:
        swc_path = Path(swc_path)
        nrrd_path = swc_path.with_suffix(".nrrd")

        # Get template ID from parent directory name
        template_id = swc_path.parent.name
        template_path = get_template_path(template_id)

        print(f"\nProcessing: {swc_path}")
        print(f"  Template ID: {template_id}")
        print(f"  Template path: {template_path}")

        # Check template exists
        if not os.path.exists(template_path):
            return str(swc_path), False, f"Template not found: {template_path}"

        # Get template shape for validation
        template_data, _ = nrrd.read(template_path)
        template_shape = template_data.shape

        # Check if NRRD needs to be created/replaced
        if not redo:
            valid, reason = is_valid_nrrd(str(nrrd_path), template_shape)
            if valid:
                print(f"  Skipping: NRRD already valid")
                return str(swc_path), True, "already valid"
            else:
                print(f"  NRRD invalid ({reason}), will regenerate")

        # Strip leading whitespace from SWC (like the sed command)
        strip_leading_whitespace(str(swc_path))

        # Remove old derived files
        clean_derived_files(swc_path)

        # Convert
        success = convert_swc_to_nrrd(str(swc_path), template_path, str(nrrd_path))

        if success:
            return str(swc_path), True, "converted successfully"
        else:
            return str(swc_path), False, "conversion produced empty volume"

    except Exception as e:
        import traceback

        traceback.print_exc()
        return str(swc_path), False, f"exception: {e}"


def find_swc_files():
    """Find all volume.swc files in VFBu directories."""
    pattern = "/IMAGE_PRIVATE/VFBu_*/VFB_*/volume.swc"
    return sorted(glob.glob(pattern))


def main():
    parser = argparse.ArgumentParser(description="Convert SWC files to NRRD volumes")
    parser.add_argument("--redo", action="store_true", help="Regenerate all files, even valid ones")
    parser.add_argument("--dry-run", action="store_true", help="Just list files, don't process")
    args = parser.parse_args()

    print("Searching for SWC files in /IMAGE_PRIVATE/VFBu_*/VFB_*/...")
    swc_files = find_swc_files()
    print(f"Found {len(swc_files)} SWC files")

    if not swc_files:
        print("No SWC files found")
        return 0

    if args.dry_run:
        print("\nDry run - files that would be processed:")
        for swc_path in swc_files:
            nrrd_path = Path(swc_path).with_suffix('.nrrd')
            template_id = Path(swc_path).parent.name
            template_path = get_template_path(template_id)

            if os.path.exists(template_path):
                template_data, _ = nrrd.read(template_path)
                valid, reason = is_valid_nrrd(str(nrrd_path), template_data.shape)
            else:
                valid, reason = False, "template missing"

            status = "SKIP (valid)" if valid and not args.redo else f"PROCESS ({reason})"
            print(f"  {swc_path}: {status}")
        return 0

    # Process files
    results = {"success": [], "failed": [], "skipped": []}

    for swc_path in swc_files:
        path, success, message = process_swc_file(swc_path, redo=args.redo)

        if "already valid" in message:
            results["skipped"].append((path, message))
        elif success:
            results["success"].append((path, message))
        else:
            results["failed"].append((path, message))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total SWC files: {len(swc_files)}")
    print(f"Skipped (already valid): {len(results['skipped'])}")
    print(f"Successfully converted: {len(results['success'])}")
    print(f"Failed: {len(results['failed'])}")

    if results["failed"]:
        print("\nFailed files:")
        for path, message in results["failed"]:
            print(f"  {path}: {message}")
            #TBD update error message to solr record.
        return 0  # failures shouldn't stop processing.

    return 0


if __name__ == "__main__":
    sys.exit(main())
