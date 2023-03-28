import numpy as np
import nrrd
import argparse
from math import pi
import pandas as pd

def convert_swc_to_nrrd(swc_file, template_file, output_file):
    # Load SWC file using pandas
    swc_data = pd.read_csv(swc_file, delim_whitespace=True, comment='#', header=None)
    
    # Replace 'NA' values with -1 
    swc_data = swc_data.replace('NA', -1)  
    
    # Convert the pandas DataFrame to a NumPy array
    swc_data = swc_data.to_numpy()
    
    # Load template NRRD file
    data, header = nrrd.read(template_file)
    # Get the dimensions of the volume
    dims = header['sizes']
    # Get the direction vectors for each axis
    directions = header['space directions']
    
    # Get the voxel sizes from the space directions of the template NRRD file
    voxel_size = [np.linalg.norm(direction) for direction in directions]
    
    # Create a new volume for the SWC data
    volume = np.zeros(dims)
    
    # Draw each point in the SWC file as a sphere
    for i in range(swc_data.shape[0]):
        point = np.floor(np.divide(swc_data[i, 2:5],voxel_size)).astype(int)
        radius = swc_data[i, 5]
        label = swc_data[i, 1]
        parent = swc_data[i, 6]
        
        # If the point is a soma, draw it as a sphere
        if label == 1:
            # Get the coordinates of each voxel within the sphere
            x_range = np.arange(-np.divide(radius,voxel_size[0]), np.divide(radius,voxel_size[0])+1)
            y_range = np.arange(-np.divide(radius,voxel_size[1]), np.divide(radius,voxel_size[1])+1)
            z_range = np.arange(-np.divide(radius,voxel_size[2]), np.divide(radius,voxel_size[2])+1)
            xv, yv, zv = np.meshgrid(x_range, y_range, z_range, indexing='ij')
            coords = np.array([xv.flatten(), yv.flatten(), zv.flatten()]).T
            dist = np.linalg.norm(coords, axis=1)
            sphere_mask = dist <= radius
            
            # Convert sphere coordinates to volume coordinates
            sphere_coords = (coords[sphere_mask] + point).T
            
            # Set the value of the volume at the sphere coordinates to 255
            clipped_coords = np.stack([
                np.clip(np.floor(sphere_coords[0]).astype(int), 0, dims[0] - 1),
                np.clip(np.floor(sphere_coords[1]).astype(int), 0, dims[1] - 1),
                np.clip(np.floor(sphere_coords[2]).astype(int), 0, dims[2] - 1)
            ], axis=-1)
            volume[clipped_coords[:, 0], clipped_coords[:, 1], clipped_coords[:, 2]] = 255
            
            # Otherwise, draw the point as a single voxel
        else:
            # Convert point coordinates to volume coordinates
            point -= 1  # SWC format starts indexing at 1
            point = np.dot(directions, point)
            point = point.astype(int)

            # Clip the point coordinates to ensure they are within the valid range
            clipped_point = np.clip(point, 0, dims - 1)

            # Set the value of the volume at the clipped point coordinates to 255
            volume[clipped_point[0], clipped_point[1], clipped_point[2]] = 255

    
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
