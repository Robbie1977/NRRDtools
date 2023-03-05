import numpy as np
import nrrd
import os
from multiprocessing import Pool

def process_chunk(args):
    """
    Process a chunk of vertices and create a binary mesh for each chunk.
    :param args: tuple, contains the arguments to be processed by this function
    :return: numpy.ndarray, the binary mesh created from this chunk
    """
    vertices, radius, grid_shape, scale_factor = args
    mesh = np.zeros(grid_shape, dtype=bool)
    scaled_vertices = np.round(vertices).astype(int) - 1
    mesh[tuple(scaled_vertices.T)] = True
    if radius is not None:
        for vertex in vertices:
            indices = np.indices(grid_shape)
            distances = np.linalg.norm(indices - np.round(vertex / scale_factor).astype(int).reshape(3, 1, 1, 1), axis=0)
            mask = distances <= radius / scale_factor[0]
            mesh[mask] = True
    return mesh

def obj_to_nrrd(input_file, output_file=None, extent=None, radius=None, num_workers=None):
    """
    Convert an OBJ file to a binary NRRD file with a physical size of 1 micron per voxel and microns as the unit for each axis.
    :param input_file: str, path to the input OBJ file
    :param output_file: str (optional), path to the output NRRD file. If not specified, the output file will have the same name as the input file but with the '.nrrd' extension
    :param extent: tuple (optional), the extent of the voxel grid. If not specified, the extent will be calculated based on the maximum vertex coordinates in the OBJ file.
    :param radius: float (optional), the radius of the sphere of voxels to mark as True for each vector point.
    :param num_workers: int (optional), the number of worker processes to use for parallel processing. If not specified, uses a single process.
    """
    if output_file is None:
        output_file = os.path.splitext(input_file)[0] + '.nrrd'
    vertices = []
    with open(input_file, 'r') as f:
        for line in f:
            if line.startswith('v '):
                vertex = [float(x) for x in line.strip().split()[1:]]
                vertices.append(vertex)
    if extent is None:
        max_coord = np.ceil(np.max(vertices, axis=0)).astype(int)
        grid_shape = tuple(max_coord)
    else:
        grid_shape = tuple(extent)
    scale_factor = np.ones(3, dtype=float)
    if radius is not None:
        chunks = np.array_split(vertices, num_workers)
        with Pool(num_workers) as pool:
            results = pool.map(process_chunk, [(chunk, radius, grid_shape, scale_factor) for chunk in chunks])
        mesh = np.zeros(grid_shape, dtype=bool)
        for result in results:
            mesh |= result
    else:
        mesh = np.zeros(grid_shape, dtype=bool)
        scaled_vertices = np.round(vertices).astype(int) - 1
        mesh[tuple(scaled_vertices.T)] = True
    matrix = mesh.astype(np.uint8) * 255
    header = {
        'encoding': 'gzip',
        'space': 'right-anterior-superior',
        'space directions': [(1.0, 0, 0), (0, 1.0, 0), (0, 0, 1.0)],
        'space units': ['microns', 'microns', 'microns'],
        'kinds': ['domain', 'domain', 'domain']
    }
    nrrd.write(output_file, matrix, header)

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python obj_to_nrrd.py input.obj [output.nrrd] ['(X,Y,Z)'] [radius]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = None
    extent = None
    radius = None
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    if len(sys.argv) > 3:
        extent = sys.argv[3]
        extent = tuple(map(int, extent.strip("()").split(",")))
    
    if len(sys.argv) > 4:
        radius = int(sys.argv[4])

    obj_to_nrrd(input_file, output_file=output_file, extent=extent, radius=radius)
