import numpy as np
import nrrd

import numpy as np
import nrrd

def convert_swc_to_nrrd(swc_file, template_file, output_file):
    # Load the template nrrd file
    data, header = nrrd.read(template_file)
    voxel_size = header['space directions'][0][0]

    # Load the swc file
    swc_data = np.loadtxt(swc_file, dtype=np.float32, comments='#', usecols=(2, 3, 4, 5, 6), ndmin=2)

    # Create an empty volume
    volume_shape = data.shape
    volume = np.zeros(volume_shape, dtype=np.uint8)

    # Fill in the volume with the swc data
    for i in range(swc_data.shape[0]):
        x, y, z, radius, parent = swc_data[i]
        x = int(round(x / voxel_size))
        y = int(round(y / voxel_size))
        z = int(round(z / voxel_size))
        radius = int(round(radius / voxel_size))
        if i > 0:
            parent = int(parent) - 1
            child = np.array([x, y, z])
            parent_point = swc_data[parent, :3]
            parent_point = np.array(parent_point)
            direction = child - parent_point
            distance = np.linalg.norm(direction)
            direction = direction / distance
            for j in range(1, int(distance)):
                point = parent_point + j * direction
                point = np.round(point).astype(int)
                volume[point[0], point[1], point[2]] = 255
        volume[x, y, z] = 255

    # Save the output file
    nrrd.write(output_file, volume, header=header)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Convert a SWC file to an NRRD file")
    parser.add_argument("swc_file", help="Path to SWC file")
    parser.add_argument("template_file", help="Path to template NRRD file")
    parser.add_argument("output_file", help="Path to output NRRD file")
    args = parser.parse_args()
    convert_swc_to_nrrd(args.swc_file, args.template_file, args.output_file)
