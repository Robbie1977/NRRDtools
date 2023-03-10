import numpy as np
import nrrd
import argparse
from math import pi

def convert_swc_to_nrrd(swc_file, template_file, output_file):
    # Load the SWC data
    swc_data = np.loadtxt(swc_file, comments='#')

    # Load the template image and extract the voxel dimensions
    template, options = nrrd.read(template_file)
    voxel_size = options['spacings']

    # Calculate the dimensions of the output volume
    dims = template.shape

    # Create an empty volume
    volume = np.zeros(dims, dtype=np.uint8)

    # Loop through the SWC data and draw lines between each point and its parent
    for i in range(len(swc_data)):
        # Extract the X, Y, and Z coordinates
        x = int(swc_data[i, 2] / voxel_size[0])
        y = int(swc_data[i, 3] / voxel_size[1])
        z = int(swc_data[i, 4] / voxel_size[2])

        # If this is the soma, draw it as a sphere with the given radius
        if swc_data[i, 1] == 1:
            radius = int(swc_data[i, 5] / voxel_size[0])
            for xi in range(max(0, x-radius), min(dims[0], x+radius)):
                for yi in range(max(0, y-radius), min(dims[1], y+radius)):
                    for zi in range(max(0, z-radius), min(dims[2], z+radius)):
                        if (xi-x)**2 + (yi-y)**2 + (zi-z)**2 <= radius**2:
                            volume[xi, yi, zi] = 255
        # Otherwise, draw a line to the parent
        else:
            parent = int(swc_data[i, 6])
            if parent >= 0:
                parent_x = int(swc_data[parent-1, 2] / voxel_size[0])
                parent_y = int(swc_data[parent-1, 3] / voxel_size[1])
                parent_z = int(swc_data[parent-1, 4] / voxel_size[2])
                direction = [x - parent_x, y - parent_y, z - parent_z]
                distance = np.sqrt(direction[0]**2 + direction[1]**2 + direction[2]**2)
                direction = [d / distance for d in direction]
                for j in range(int(distance)):
                    xi = int(parent_x + j * direction[0])
                    yi = int(parent_y + j * direction[1])
                    zi = int(parent_z + j * direction[2])
                    volume[xi, yi, zi] = 255

    # Save the output volume as an NRRD file
    nrrd.write(output_file, volume, options=options)

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
