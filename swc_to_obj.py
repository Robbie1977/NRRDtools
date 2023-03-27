import numpy as np
import trimesh
import math

def read_swc(file_path):
    return np.loadtxt(file_path, delimiter=' ', comments='#',
                      dtype={'names': ('id', 'type', 'x', 'y', 'z', 'radius', 'parent'),
                             'formats': ('i4', 'i4', 'f4', 'f4', 'f4', 'f4', 'i4')})

def create_mesh_from_swc(swc_data):
    # Create an empty list to store all mesh objects
    meshes = []

    # Process nodes
    for i, node in enumerate(swc_data):
        # Create a sphere for each node
        sphere = trimesh.creation.icosphere(subdivisions=2, radius=node['radius'])
        sphere.apply_translation([node['x'], node['y'], node['z']])
        meshes.append(sphere)

        # Create a cylinder for each edge
        if node['parent'] != -1:
            parent_node = swc_data[np.where(swc_data['id'] == node['parent'])[0][0]]

            # Calculate cylinder properties
            start = np.array([node['x'], node['y'], node['z']])
            end = np.array([parent_node['x'], parent_node['y'], parent_node['z']])
            length = np.linalg.norm(end - start)
            direction = (end - start) / length
            radius = (node['radius'] + parent_node['radius']) / 2

            # Create the cylinder
            cylinder = trimesh.creation.cylinder(radius=radius, height=length, sections=16)
            cylinder.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], direction))
            cylinder.apply_translation((start + end) / 2)

            # Add the cylinder to the list of meshes
            meshes.append(cylinder)

    # Combine all the meshes into a single mesh object
    combined_mesh = trimesh.util.concatenate(meshes)

    return combined_mesh

def convert_swc_to_obj(swc_file, obj_file):
    swc_data = read_swc(swc_file)
    mesh = create_mesh_from_swc(swc_data)
    mesh.export(obj_file)

if __name__ == "__main__":
    # Create argument parser
    parser = argparse.ArgumentParser(description="Convert SWC file to OBJ file")
    
    # Add arguments
    parser.add_argument("swc_file", help="Path to input SWC file")
    parser.add_argument("output_file", help="Path to output OBJ file")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Read SWC data
    swc_data = read_swc(args.swc_file)

    # Create mesh from SWC data
    mesh = create_mesh_from_swc(swc_data)
    
    # Save mesh as OBJ file
    mesh.export(args.output_file, file_type='obj')

    
    
# # Example usage
# swc_file = 'path/to/your/input.swc'
# obj_file = 'path/to/your/output.obj'

# convert_swc_to_obj(swc_file, obj_file)
