import numpy as np
import nrrd
import argparse
from math import pi
import pandas as pd
import trimesh
import trimesh.voxel.creation


def read_swc(file_path):
    # Load SWC file using pandas
    swc_data = pd.read_csv(file_path, delim_whitespace=True, comment='#', header=None)

    # Replace 'NA' and 'nan' values with -1
    swc_data = swc_data.replace(['NA', np.nan], -1)

    # Convert the pandas DataFrame to a NumPy array
    swc_data = swc_data.to_numpy()

    # Create a structured array with the specified header
    swc_data = np.core.records.fromarrays(swc_data.T,
                                          names='id, type, x, y, z, radius, parent',
                                          formats='i4, i4, f4, f4, f4, f4, i4')
    
    return swc_data

def create_volume_from_swc(swc_data, dims, voxel_size, minRadius=0.005):
    volume = np.zeros(dims).astype(np.uint8)

    for node in swc_data:
        sphere = trimesh.creation.icosphere(subdivisions=2, radius=max(node['radius'], minRadius))
        sphere.apply_translation([node['x'], node['y'], node['z']])
        
        sphere_vox = trimesh.voxel.creation.voxelize(sphere, pitch=voxel_size)
        sphere_indices = sphere_vox.indices
        valid_indices = np.all((sphere_indices >= 0) & (sphere_indices < dims), axis=1)
        sphere_indices = sphere_indices[valid_indices]
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

            cylinder_vox = trimesh.voxel.creation.voxelize(cylinder, pitch=voxel_size)
            cylinder_indices = cylinder_vox.indices
            valid_indices = np.all((cylinder_indices >= 0) & (cylinder_indices < dims), axis=1)
            cylinder_indices = cylinder_indices[valid_indices]
            volume[cylinder_indices[:, 0], cylinder_indices[:, 1], cylinder_indices[:, 2]] = 255

    return volume


def convert_swc_to_nrrd(swc_file, template_file, output_file):
    swc_data = read_swc(swc_file)
    data, header = nrrd.read(template_file)
    dims = header['sizes']
    directions = header['space directions']
    voxel_size = [np.linalg.norm(direction) for direction in directions]

    volume = create_volume_from_swc(swc_data, dims, voxel_size)
    
    # Convert the volume to uint8
    volume = volume.astype(np.uint8)

    # Write the output NRRD file
    nrrd.write(output_file, volume, header=header)
    
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
