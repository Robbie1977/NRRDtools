import sys
import numpy as np
import nrrd
import os
import trimesh


def obj_to_nrrd(input_file, template_nrrd, output_file=None):
    """
    Convert an OBJ file to a binary NRRD file with the voxel size, space directions, and mesh size of a template NRRD file.
    :param input_file: str, path to the input OBJ file
    :param template_nrrd: str, path to the template NRRD file
    :param output_file: str (optional), path to the output NRRD file. If not specified, the output file will have the same name as the input file but with the '.nrrd' extension
    """
    # Check if output file path is specified. If not, use the default output file name
    if output_file is None:
        output_file = os.path.splitext(input_file)[0] + '.nrrd'
    
    # Load vertex data from OBJ file and create trimesh
    vertices = []
    faces = []
    with open(input_file, 'r') as f:
        for line in f:
            if line.startswith('v '):
                vertex = [float(x) for x in line.strip().split()[1:]]
                vertices.append(vertex)
            elif line.startswith('f '):
                face = [int(x.split('/')[0])-1 for x in line.strip().split()[1:]]
                faces.append(face)
    trimesh_mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)

    # Read the template NRRD file and extract the header and data size
    template_data, template_header = nrrd.read(template_nrrd)
    space_directions = template_header['space directions']
    space_units = template_header['space units']
    template_shape = template_data.shape

    # Create a voxel grid that matches the shape of the template NRRD file's data
    mesh = np.zeros(template_shape, dtype=bool)
    
    # Get the voxel sizes from the space directions of the template NRRD file
    voxel_size = [np.linalg.norm(direction) for direction in space_directions]
    
    # Voxelized mesh using a pitch of 1.0
    volume = trimesh_mesh.voxelized(1.0).fill()
    
    # Clip the voxel indices to be within the bounds of the template shape
    voxel_indices = np.clip(np.floor(np.divide(volume.points,voxel_size)).astype(int), 0, np.array(template_shape) - 1)
    mesh[voxel_indices[:, 0], voxel_indices[:, 1], voxel_indices[:, 2]] = True

    # Convert binary mesh to uint8 matrix
    matrix = mesh.astype(np.uint8) * 255
    
    # Set NRRD header with space directions and units from the template NRRD file
    header = template_header

    # Save uint8 matrix as NRRD file using nrrd.write
    nrrd.write(output_file, matrix, header)
    
    print(f"Saved NRRD file: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python obj_to_nrrd.py input.obj template.nrrd [output.nrrd]")
        sys.exit(1)

    input_file = sys.argv[1]
    template_nrrd = sys.argv[2]
    output_file = None

    if len(sys.argv) > 3:
        output_file = sys.argv[3]

    obj_to_nrrd(input_file, template_nrrd, output_file)
