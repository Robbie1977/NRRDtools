import numpy as np
import nrrd
import os
import multiprocessing
from multiprocessing import Pool
import threading

def process_chunk(args):
    """
    vertices, radius, grid_shape, scale_factor, progress_queue = args
    Process a chunk of vertices and create a binary mesh for each chunk.
    :param args: tuple, contains the arguments to be processed by this function
    :return: numpy.ndarray, the binary mesh created from this chunk
    """
    vertices, radius, grid_shape, scale_factor, progress_queue = args
    mesh = np.zeros(grid_shape, dtype=bool)
    scaled_vertices = np.round(vertices).astype(int) - 1
    mesh[tuple(scaled_vertices.T)] = True
    if radius is not None:
        for i, vertex in enumerate(vertices):
            indices = np.indices(grid_shape)
            distances = np.linalg.norm(indices - np.round(vertex / scale_factor).astype(int).reshape(3, 1, 1, 1), axis=0)
            mask = distances <= radius / scale_factor[0]
            mesh[mask] = True
            progress_queue.put((i, len(vertices)))
    return mesh

def obj_to_nrrd(input_file, output_file=None, extent=None, voxel_size=None, radius=None, num_workers=1):
    """
    Convert an OBJ file to a binary NRRD file with a specified voxel size and microns as the unit for each axis.
    :param input_file: str, path to the input OBJ file
    :param output_file: str (optional), path to the output NRRD file. If not specified, the output file will have the same name as the input file but with the '.nrrd' extension
    :param extent: tuple (optional), the extent of the voxel grid. If not specified, the extent will be calculated based on the maximum vertex coordinates in the OBJ file.
    :param voxel_size: tuple (optional), the physical size of each voxel in microns. If not specified, the default voxel size of 1 micron per voxel will be used.
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
    if voxel_size is None:
        voxel_size = (1.0, 1.0, 1.0)
    scale_factor = np.array(voxel_size) / 1000.0  # Convert from microns to millimeters
    if radius is not None:
        chunks = np.array_split(vertices, num_workers)
        with Pool(num_workers) as pool:
            results = []
            progress_queue = multiprocessing.Manager().Queue()
            for i, result in enumerate(pool.imap_unordered(process_chunk, [(chunk, radius, grid_shape, scale_factor, progress_queue) for chunk in chunks])):
                results.append(result)
                print_progress(i + 1, len(chunks))
            mesh = np.zeros(grid_shape, dtype=bool)
            for result in results:
                mesh |= result
    else:
        mesh = np.zeros(grid_shape, dtype=bool)
        scaled_vertices = np.round(vertices).astype(int) - 1
        mesh[tuple(scaled_vertices.T)] = True
    # Flip the mesh along the X and Y axes to correct the origin
    mesh = np.flip(mesh, axis=(0, 1))
    matrix = mesh.astype(np.uint8) * 255
    header = {
        'encoding': 'gzip',
        'space': 'right-anterior-superior',
        'space directions': [(voxel_size[0], 0, 0), (0, voxel_size[1], 0), (0, 0, voxel_size[2])],
        'space units': ['microns', 'microns', 'microns'],
        'kinds': ['domain', 'domain', 'domain']
    }
    nrrd.write(output_file, matrix, header)
    
def print_progress(iteration, total):
    """
    Print progress during execution of a loop.
    :param iteration: int, current iteration (0-based)
    :param total: int, total number of iterations
    """
    percent = "{:.1f}".format(100 * (iteration / float(total)))
    filled_length = int(50 * iteration // total)
    bar = '#' * filled_length + '-' * (50 - filled_length)
    print(f'\rProgress |{bar}| {percent}% Complete', end='\r')
    if iteration == total:
        print('\n')

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python obj_to_nrrd.py input.obj [output.nrrd] ['(X,Y,Z)'] [radius] ['(voxel_size_x, voxel_size_y, voxel_size_z)']")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = None
    extent = None
    radius = None
    voxel_size = None

    if len(sys.argv) > 2:
        output_file = sys.argv[2]

    if len(sys.argv) > 3:
        extent = sys.argv[3]
        extent = tuple(map(int, extent.strip("()").split(",")))

    if len(sys.argv) > 4:
        radius = float(sys.argv[4])

    if len(sys.argv) > 5:
        voxel_size = sys.argv[5]
        voxel_size = tuple(map(float, voxel_size.strip("()").split(",")))

    obj_to_nrrd(input_file, output_file=output_file, extent=extent, voxel_size=voxel_size, radius=radius, num_workers=5)

