def obj_to_nrrd(input_file, output_file=None, extent=None):
    """
    Convert an OBJ file to a binary NRRD file with a physical size of 1 micron per voxel and microns as the unit for each axis.

    :param input_file: str, path to the input OBJ file
    :param output_file: str (optional), path to the output NRRD file. If not specified, the output file will have the same name as the input file but with the '.nrrd' extension
    :param extent: tuple (optional), the extent of the voxel grid. If not specified, the extent will be calculated based on the maximum vertex coordinates in the OBJ file.
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

    # Calculate the extent of the voxel grid
    if extent is None:
        max_coord = np.ceil(np.max(vertices, axis=0)).astype(int)
        grid_shape = tuple(max_coord)
    else:
        grid_shape = tuple(extent)

    # Create a binary mesh
    mesh = np.zeros(grid_shape, dtype=bool)

    # Set binary value to True at each vertex coordinate
    scale_factor = np.ones(3, dtype=float)  # scale factor is 1 micron per voxel
    scaled_vertices = np.round(vertices).astype(int) - 1  # subtract 1 to convert to 0-based indexing
    mesh[tuple(scaled_vertices.T)] = True

    # Convert binary mesh to uint8 matrix
    matrix = mesh.astype(np.uint8) * 255

    # Set NRRD header with 1 micron scale factor and microns as the unit for each axis
    header = {
        'encoding': 'gzip',
        'space': 'right-anterior-superior',
        'space directions': [(1.0, 0, 0), (0, 1.0, 0), (0, 0, 1.0)],
        'space units': ['microns', 'microns', 'microns'],
        'kinds': ['domain', 'domain', 'domain']
    }

    # Save uint8 matrix as NRRD file using nrrd.write
    nrrd.write(output_file, matrix, header)

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python obj_to_nrrd.py input.obj [output.nrrd]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = None
    extent=None
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    if len(sys.argv) > 3:
        extent = sys.argv[3]

    obj_to_nrrd(input_file, output_file=output_file, extent=extent)
