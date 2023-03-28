import argparse
import numpy as np
import trimesh
import nrrd
import pandas as pd
import trimesh.voxel.creation
import scipy.ndimage

def read_swc(file_path):
    swc_data = pd.read_csv(file_path, delim_whitespace=True, comment='#', header=None)
    swc_data = swc_data.replace(['NA', np.nan], -1)
    swc_data = swc_data.to_numpy()
    swc_data = np.core.records.fromarrays(swc_data.T, names='id, type, x, y, z, radius, parent', formats='i4, i4, f4, f4, f4, f4, i4')
    return swc_data

def create_volume_from_swc(swc_data, dims, voxel_size, minRadius=0.005):
    volume = np.zeros(dims).astype(np.uint8)
    pitch = 1.0

    for node in swc_data:
        sphere = trimesh.creation.icosphere(subdivisions=2, radius=max(node['radius'], minRadius))
        sphere.apply_translation([node['x'], node['y'], node['z']])
        sphere_vox = trimesh.voxel.creation.voxelize(sphere, pitch=pitch)
        sphere_indices = sphere_vox.sparse_indices.astype(int)
        volume[sphere_indices[:, 0], sphere_indices[:, 1], sphere_indices[:, 2]] = 255

        if node['parent'] != -1:
            parent_node = swc_data[np.where(swc_data['id'] == node['parent'])[0][0]]
            start = np.array([node['x'], node['y'], node['z']])
            end = np.array([parent_node['x'], parent_node['y'], parent_node['z']])
            length = np.linalg.norm(end - start)
            direction = (end - start) / length
            radius = (max(node['radius'], minRadius) + max(parent_node['radius'], minRadius)) / 2
            cylinder = trimesh.creation.cylinder(radius=max(radius, minRadius), height=length, sections=16)
            cylinder.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], direction))
            cylinder.apply_translation((start + end) / 2)
            cylinder_vox = trimesh.voxel.creation.voxelize(cylinder, pitch=pitch)
            cylinder_indices = cylinder_vox.sparse_indices.astype(int)
            volume[cylinder_indices[:, 0], cylinder_indices[:, 1], cylinder_indices[:, 2]] = 255

    # Scale the volume by the voxel_size
    scaled_volume = scipy.ndimage.zoom(volume, voxel_size, order=0)

    return scaled_volume


def convert_swc_to_nrrd(swc_file, template_file, output_file):
    swc_data = read_swc(swc_file)
    max_coords = np.max(np.array([swc_data['x'], swc_data['y'], swc_data['z']]), axis=1)
    print(f"Max SWC coordinates: {max_coords}")

    nrrd_template, options = nrrd.read(template_file)
    space_directions = options['space directions']
    voxel_size = [np.linalg.norm(direction) for direction in space_directions]
    dims = np.ceil(np.multiply(np.shape(nrrd_template),voxel_size)).astype(int)

    print(f"Micron space image shape: {dims}")

    volume = create_volume_from_swc(swc_data, dims, voxel_size)
    
    

    nonzero_indices = np.nonzero(volume)
    max_volume_coords = np.max(np.column_stack(nonzero_indices), axis=0)
    print(f"Max volume coordinates: {max_volume_coords}")

    print(f"Output image shape: {np.shape(volume)}")

    nrrd.write(output_file, volume.astype(np.uint8), header=options)

    print(f"Saved NRRD file: {output_file}")

if __name__ == "__main__":
    # Create argument parser
    parser = argparse.ArgumentParser(description="Convert SWC file to NRRD file")
    
    # Add arguments
    parser.add_argument("swc_file", help="Path to input SWC file")
    parser.add_argument("template_file", help="Path to input template NRRD file")
    parser.add_argument("output_file", help="Path to output NRRD file")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Convert SWC to NRRD
    convert_swc_to_nrrd(args.swc_file, args.template_file, args.output_file)
