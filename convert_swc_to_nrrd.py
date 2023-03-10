import numpy as np
import nrrd

def convert_swc_to_nrrd(swc_file, template_file, output_file):
    # Load the SWC file
    with open(swc_file) as f:
        swc_lines = f.readlines()
        
    # Extract the coordinates and radii from the SWC file
    coords = []
    radii = []
    for line in swc_lines:
        if line.startswith('#'):
            continue
        data = line.strip().split()
        coords.append([float(data[2]), float(data[3]), float(data[4])])
        radii.append(float(data[5]))

    # Load the template file to get the voxel size and dimensions
    template_data, template_header = nrrd.read(template_file)
    voxel_size = template_header['space directions'][0][0]
    dimensions = template_data.shape

    # Create the output NRRD file with the same dimensions and voxel size as the template
    output_data = np.zeros(dimensions, dtype=np.uint8)
    output_header = {
        'type': 'uint8',
        'dimension': 3,
        'space': 'left-posterior-superior',
        'sizes': dimensions,
        'space directions': np.array([[voxel_size,0,0],[0,voxel_size,0],[0,0,voxel_size]]),
        'encoding': 'gzip'
    }

    # Draw each line segment in the SWC file
    for i in range(1, len(coords)):
        parent = coords[i-1]
        child = coords[i]
        parent_radius = radii[i-1] / 2
        child_radius = radii[i] / 2
        direction = child - parent
        distance = np.linalg.norm(direction)
        direction = direction / distance
        num_steps = int(np.ceil(distance / voxel_size))
        for j in range(num_steps):
            step = parent + (j / num_steps) * direction * distance
            output_data[int(round(step[0]/voxel_size)), int(round(step[1]/voxel_size)), int(round(step[2]/voxel_size))] = child_radius
            for k in range(1, int(round(parent_radius/voxel_size))):
                output_data[int(round(parent[0]/voxel_size)), int(round(parent[1]/voxel_size)), int(round(parent[2]/voxel_size))] = 255 - (255 * k / int(round(parent_radius/voxel_size)))

    # Write the output NRRD file
    nrrd.write(output_file, output_data, output_header)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Convert a SWC file to an NRRD file")
    parser.add_argument("swc_file", help="Path to SWC file")
    parser.add_argument("template_file", help="Path to template NRRD file")
    parser.add_argument("output_file", help="Path to output NRRD file")
    args = parser.parse_args()
    convert_swc_to_nrrd(args.swc_file, args.template_file, args.output_file)
