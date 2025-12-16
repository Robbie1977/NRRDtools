#!/usr/bin/env python3
import argparse
import numpy as np
import nrrd
import navis
import os

def convert_swc_to_nrrd(swc_file, template_file, output_file):
    # Read the template to get dimensions and spatial info
    template_data, template_header = nrrd.read(template_file)
    
    # Get voxel size from template
    space_directions = template_header['space directions']
    voxel_size = np.array([np.linalg.norm(d) for d in space_directions])
    origin = np.array(template_header.get('space origin', [0, 0, 0]))
    
    print(f"Template shape: {template_data.shape}")
    print(f"Voxel size: {voxel_size}")
    print(f"Origin: {origin}")
    
    # Read SWC file with navis
    neuron = navis.read_swc(swc_file)
    print(f"Loaded neuron with {len(neuron.nodes)} nodes")
    print(f"Bounding box (microns): {neuron.bbox}")
    
    # Convert from microns to voxel coordinates
    # voxel = (micron - origin) / voxel_size
    neuron.nodes[['x', 'y', 'z']] = (neuron.nodes[['x', 'y', 'z']] - origin) / voxel_size
    print(f"Bounding box (voxels): {neuron.bbox}")
    
    # Voxelize at pitch=1 (now in voxel space)
    bounds = np.array([[0, template_data.shape[0]], [0, template_data.shape[1]], [0, template_data.shape[2]]])
    voxel_neuron = navis.voxelize(
        neuron,
        pitch=1,
        bounds=bounds
    )
    
    # Get volume as numpy array
    volume = voxel_neuron.grid.astype(np.uint8)
    volume[volume > 0] = 255
    
    # Ensure volume shape matches template shape
    volume = volume[:template_data.shape[0], :template_data.shape[1], :template_data.shape[2]]
    
    print(f"Output shape: {volume.shape}")
    print(f"Non-zero voxels: {np.count_nonzero(volume)}")
    
    if np.count_nonzero(volume) == 0:
        print("WARNING: No voxels were filled - check SWC coordinates vs template space")
        return False
    
    # Build output header explicitly preserving spatial metadata
    output_header = {
        'type': 'uint8',
        'dimension': 3,
        'sizes': volume.shape,
        'encoding': template_header.get('encoding', 'gzip'),
    }
    
    # Copy spatial metadata from template
    if 'space' in template_header:
        output_header['space'] = template_header['space']
    if 'space directions' in template_header:
        output_header['space directions'] = template_header['space directions']
    if 'space origin' in template_header:
        output_header['space origin'] = template_header['space origin']
    if 'kinds' in template_header:
        output_header['kinds'] = template_header['kinds']
    
    # Write output
    nrrd.write(output_file, volume, header=output_header)
    print(f"Saved: {output_file}")
    
    # Set permissions
    os.chmod(output_file, 0o777)
    
    # Verify the output
    _, verify_header = nrrd.read(output_file)
    print(f"Verified output header:")
    for key in ['space', 'space directions', 'space origin', 'sizes']:
        if key in verify_header:
            print(f"  {key}: {verify_header[key]}")
    
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert SWC file to NRRD file using navis")
    parser.add_argument("swc_file", help="Path to input SWC file")
    parser.add_argument("template_file", help="Path to input template NRRD file")
    parser.add_argument("output_file", help="Path to output NRRD file")
    args = parser.parse_args()
    
    convert_swc_to_nrrd(args.swc_file, args.template_file, args.output_file)
