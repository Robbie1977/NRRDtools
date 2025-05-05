import argparse
import numpy as np
import trimesh
import nrrd
import pandas as pd
import trimesh.voxel.creation
import scipy.ndimage

def read_swc(file_path):
    swc_data = pd.read_csv(file_path, sep='\s+', comment='#', header=None)
    swc_data = swc_data.replace(['NA', np.nan], -1)
    swc_data = swc_data.to_numpy()
    swc_data = np.core.records.fromarrays(swc_data.T, names='id, type, x, y, z, radius, parent', formats='i4, i4, f4, f4, f4, f4, i4')
    return swc_data

def create_volume_from_swc(swc_data, dims, voxel_size, minRadius=0.005):
    pitch = minRadius * 0.5
    scaling_factor = 4  # The voxel size will now be 0.25x0.25x0.25 microns
    # Scale the dims by the desired factor
    scaled_dims = (dims * scaling_factor).astype(int)
    volume = np.zeros(scaled_dims, dtype=np.uint8)

    for node in swc_data:
        # Only create a sphere for soma nodes (type == 1)
        if node['type'] == 1:
            sphere = trimesh.creation.icosphere(subdivisions=2, radius=max(node['radius'], minRadius * scaling_factor))
            sphere_vox = trimesh.voxel.creation.voxelize(sphere, pitch=pitch, max_iter=20)
            sphere_indices = sphere_vox.sparse_indices.astype(float)
            sphere_indices += np.array([node['x'], node['y'], node['z']])
            sphere_indices *= scaling_factor
            sphere_indices = np.round(sphere_indices).astype(int)
            sphere_indices = np.clip(sphere_indices, [0, 0, 0], np.array(scaled_dims) - 1)
            volume[sphere_indices[:, 0], sphere_indices[:, 1], sphere_indices[:, 2]] = 255
            
        # Always create cylinders for connections (neurites)
        if node['parent'] != -1:
            parent_node = swc_data[np.where(swc_data['id'] == node['parent'])[0][0]]
            start = np.array([node['x'], node['y'], node['z']]) * scaling_factor
            end = np.array([parent_node['x'], parent_node['y'], parent_node['z']]) * scaling_factor
            length = np.linalg.norm(end - start)

            if length > 0:  # Check if the length is greater than zero before proceeding
                direction = (end - start) / length
                radius = (max(node['radius'], minRadius) + max(parent_node['radius'], minRadius)) / 2
                cylinder = trimesh.creation.cylinder(radius=max(radius * scaling_factor, minRadius * scaling_factor), height=length, sections=16)

                try:
                    cylinder.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], direction))
                except np.linalg.LinAlgError:
                    # Alternative method to align the vectors
                    axis = np.cross([0, 0, 1], direction)
                    angle = np.arccos(np.dot([0, 0, 1], direction))
                    cylinder.apply_transform(trimesh.transformations.rotation_matrix(angle, axis))

                cylinder.apply_translation((start + end) / 2)
                cylinder_vox = trimesh.voxel.creation.voxelize(cylinder, pitch=pitch, max_iter=20)
                cylinder_indices = cylinder_vox.sparse_indices.astype(float)
                cylinder_indices += np.array([(start + end) / 2])
                cylinder_indices = np.round(cylinder_indices).astype(int)
                cylinder_indices = np.clip(cylinder_indices, [0, 0, 0], np.array(scaled_dims) - 1)
                volume[cylinder_indices[:, 0], cylinder_indices[:, 1], cylinder_indices[:, 2]] = 255

    return volume

    nonzero_indices = np.nonzero(volume)
    if not np.any(nonzero_indices):
        print("Warning: No nonzero values found in the volume. Please check your input SWC file.")
    else:
        max_volume_coords = np.max(np.column_stack(nonzero_indices), axis=0)
    print(f"Max volume coordinates: {max_volume_coords}")
    # Scale the volume by the voxel_size
    scale_factor = np.divide(1 / scaling_factor, voxel_size)
    print(f"micron image shape: {volume.shape}")
    print(f"Scaling by: {scale_factor}")
    scaled_volume = scipy.ndimage.zoom(volume, scale_factor, order=0)
    print(f"scaled image shape: {scaled_volume.shape}")
    nonzero_indices = np.nonzero(scaled_volume)
    max_volume_coords = np.max(np.column_stack(nonzero_indices), axis=0)
    print(f"Max scaled_volume coordinates: {max_volume_coords}")
    return scaled_volume


def convert_swc_to_nrrd(swc_file, template_file, output_file):
    swc_data = read_swc(swc_file)
    max_coords = np.max(np.array([swc_data['x'], swc_data['y'], swc_data['z']]), axis=1)
    print(f"Max SWC coordinates: {max_coords}")

    nrrd_template, options = nrrd.read(template_file)
    space_directions = options['space directions']
    voxel_size = [np.linalg.norm(direction) for direction in space_directions]
    dims = np.round(np.multiply(np.shape(nrrd_template),voxel_size)).astype(int)

    print(f"Micron space image shape: {dims}")

    volume = create_volume_from_swc(swc_data, dims, voxel_size)
    
    if volume.shape == nrrd_template.shape:
        print("Scalling correct")
    else:
        print("Tweaking scalling")
        scale_factor = np.divide(nrrd_template.shape, volume.shape)
        print(f"micron image shape: {volume.shape}")
        print(f"Scaling by: {scale_factor}")
        scaled_volume = scipy.ndimage.zoom(volume, scale_factor, order=0)
        print(f"scaled image shape: {scaled_volume.shape}")
        volume = scaled_volume
        
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
