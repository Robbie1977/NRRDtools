import numpy as np
import nrrd
import argparse
from math import pi

def convert_swc_to_nrrd(swc_file, template_file, output_file):
    # Load SWC file
    swc_data = np.loadtxt(swc_file, comments='#')
    
    # Load template NRRD file
    data, header = nrrd.read(template_file)
    # Get the dimensions of the volume
    dims = header['sizes']
    # Get the direction vectors for each axis
    directions = header['space directions']
    
    # Create a new volume for the SWC data
    volume = np.zeros(dims)
    
    # Draw each point in the SWC file as a sphere
    for i in range(swc_data.shape[0]):
        point = swc_data[i, 2:5].astype(int)
        radius = swc_data[i, 5]
        label = swc_data[i, 1]
        
        # If the point is a soma, draw it as a sphere
        if label == 1:
            # Get the coordinates of each voxel within the sphere
            x_range = np.arange(-radius, radius+1)
            y_range = np.arange(-radius, radius+1)
            z_range = np.arange(-radius, radius+1)
            xv, yv, zv = np.meshgrid(x_range, y_range, z_range, indexing='ij')
            coords = np.array([xv.flatten(), yv.flatten(), zv.flatten()]).T
            dist = np.linalg.norm(coords, axis=1)
            sphere_mask = dist <= radius
            
            # Convert sphere coordinates to volume coordinates
            sphere_coords = (coords[sphere_mask] + point).T
            
            # Set the value of the volume at the sphere coordinates to 255
            volume[np.round(sphere_coords[0]).astype(int), np.round(sphere_coords[1]).astype(int), np.round(sphere_coords[2]).astype(int)] = 255
        # Otherwise, draw the point as a single voxel
        else:
            # Convert point coordinates to volume coordinates
            point -= 1  # SWC format starts indexing at 1
            point = np.dot(directions, point)
            point = point.astype(int)
            
            # Set the value of the volume at the point coordinates to 255
            volume[point[0], point[1], point[2]] = 255
    
    # Write the output NRRD file
    nrrd.write(output_file, volume, header=header)

def main():
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
