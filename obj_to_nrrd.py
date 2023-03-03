def obj_to_nrrd(input_file, output_file=None, fill_factor=0.05):
    """
    Convert an OBJ file to a binary NRRD file with a physical size of 1 micron per voxel and microns as the unit for each axis.

    :param input_file: str, path to the input OBJ file
    :param output_file: str (optional), path to the output NRRD file. If not specified, the output file will have the same name as the input file but with the '.nrrd' extension
    :param fill_factor: float (optional), voxel size as a fraction of the minimum dimension of the bounding box of the mesh. Default is 0.05 (1/20th of the minimum dimension).
    """
    import numpy as np
    import nrrd
    import os
    import trimesh

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

    # Translate Trimesh so its minimum coordinate values are at the origin
    min_coord = np.min(trimesh_mesh.vertices, axis=0)
    trimesh_mesh.vertices -= min_coord
    
    # Calculate the extents of the trimesh
    trimesh_extents = trimesh_mesh.bounds
    print(f"Trimesh extents: {trimesh_extents}")

    # Create a voxel grid that is large enough to fully enclose the trimesh
    max_coord = np.ceil(trimesh_mesh.bounds[1]).astype(int)
    grid_shape = tuple(max_coord)
    print(f"Voxel grid extents: {grid_shape}")
    mesh = np.zeros(grid_shape, dtype=bool)

    # Voxelized mesh and set binary values in mesh
    voxel_size = np.min(max_coord) * fill_factor
    volume = trimesh_mesh.voxelized(voxel_size).fill()
    voxel_indices = np.round(volume.points).astype(int)
    mesh[voxel_indices[:, 0]-1, voxel_indices[:, 1]-1, voxel_indices[:, 2]-1] = True

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
    if output_file is None:
        output_file = os.path.splitext(input_file)[0] + '.nrrd'
    nrrd.write(output_file, matrix, header)
    
    print(f"Saved NRRD file: {output_file}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python obj_to_nrrd.py input.obj [output.nrrd]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = None
    fill_factor = 0.005 # Note denser fill factor used 
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    if len(sys.argv) > 3:
        fill_factor = float(sys.argv[3])

    obj_to_nrrd(input_file, output_file, fill_factor)
