def obj_to_nrrd(input_file, output_file=None):
    """
    Convert an OBJ file to a binary NRRD file with a physical size of 1 micron per voxel and microns as the unit for each axis.
    
    :param input_file: str, path to the input OBJ file
    :param output_file: str (optional), path to the output NRRD file. If not specified, the output file will have the same name as the input file but with the '.nrrd' extension
    """
    import numpy as np
    import nrrd
    import os

    # Check if output file path is specified. If not, use the default output file name
    if output_file is None:
        output_file = os.path.splitext(input_file)[0] + '.nrrd'

    # Load vertex data from OBJ file
    vertices = []
    with open(input_file, 'r') as f:
        for line in f:
            if line.startswith('v '):
                vertex = [float(x) for x in line.strip().split()[1:]]
                vertices.append(vertex)

    # Convert vertex data to binary NRRD file
    max_coord = np.max(vertices, axis=0)
    grid_size = np.ceil(max_coord).astype(int) + 1  # increase grid size by 1 to avoid index out of bounds errors
    grid_shape = tuple(grid_size)
    mesh = np.zeros(grid_shape, dtype=bool)  # create an empty binary mesh
    scale_factor = grid_size / max_coord  # calculate scale factor
    scaled_vertices = vertices * scale_factor  # scale vertices to fit within grid
    mesh[np.round(scaled_vertices).astype(int)] = True  # set binary value to True at each vertex coordinate
    matrix = mesh.astype(np.uint8) * 255  # convert binary mesh to uint8 matrix
    header = {'encoding': 'gzip', 'space': 'right-anterior-superior', 'space directions': [(1.0,0,0), (0,1.0,0), (0,0,1.0)], 'space units': ['microns', 'microns', 'microns'], 'kinds': ['domain', 'domain', 'domain']}  # set NRRD header with 1 micron scale factor and microns as the unit for each axis
    nrrd.write(output_file, matrix, header)  # save uint8 matrix as NRRD file using nrrd.write

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python obj_to_nrrd.py input.obj [output.nrrd]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = None
    if len(sys.argv) > 2:
        output_file = sys.argv[2]

    obj_to_nrrd(input_file, output_file)
