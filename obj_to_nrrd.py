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

def extract_template_properties(template_file):
    """
    Extract extent and voxel size from a template NRRD file.
    :param template_file: str, path to the template NRRD file
    :return: tuple, (extent, voxel_size, header) extracted from template
    """
    try:
        template_data, template_header = nrrd.read(template_file)
        
        # Extract extent from template data shape
        extent = template_data.shape
        
        # Extract voxel size from space directions
        voxel_size = (1.0, 1.0, 1.0)  # default fallback
        if 'space directions' in template_header:
            space_dirs = template_header['space directions']
            if space_dirs is not None and len(space_dirs) >= 3:
                # Extract diagonal elements as voxel sizes
                voxel_size = tuple(abs(space_dirs[i][i]) for i in range(3))
        
        # Return relevant header fields for copying
        header_to_copy = {}
        copy_fields = ['space', 'space directions', 'space units', 'space origin', 'kinds']
        for field in copy_fields:
            if field in template_header:
                header_to_copy[field] = template_header[field]
        
        print(f"Template properties - Extent: {extent}, Voxel size: {voxel_size}")
        return extent, voxel_size, header_to_copy
        
    except Exception as e:
        print(f"Warning: Could not read template file {template_file}: {e}")
        print("Using default extent and voxel size")
        return None, None, {}

def obj_to_nrrd(input_file, output_file=None, extent=None, voxel_size=None, radius=None, num_workers=1, template_file=None):
    """
    Convert an OBJ file to a binary NRRD file with a specified voxel size and microns as the unit for each axis.
    :param input_file: str, path to the input OBJ file
    :param output_file: str (optional), path to the output NRRD file. If not specified, the output file will have the same name as the input file but with the '.nrrd' extension
    :param extent: tuple (optional), the extent of the voxel grid. If not specified, the extent will be calculated based on the maximum vertex coordinates in the OBJ file.
    :param voxel_size: tuple (optional), the physical size of each voxel in microns. If not specified, the default voxel size of 1 micron per voxel will be used.
    :param radius: float (optional), the radius of the sphere of voxels to mark as True for each vector point.
    :param num_workers: int (optional), the number of worker processes to use for parallel processing. If not specified, uses a single process.
    :param template_file: str (optional), path to a template NRRD file to extract extent and voxel size from. Overrides extent and voxel_size parameters if provided.
    """
    if output_file is None:
        output_file = os.path.splitext(input_file)[0] + '.nrrd'
    
    # If template file is provided, extract properties from it
    template_header = {}
    if template_file is not None:
        template_extent, template_voxel_size, template_header = extract_template_properties(template_file)
        if template_extent is not None:
            extent = template_extent
        if template_voxel_size is not None:
            voxel_size = template_voxel_size
    
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
    
    print(f"Processing: Grid shape = {grid_shape}, Voxel size = {voxel_size}")
    print(f"Vertex range: {np.min(vertices, axis=0)} to {np.max(vertices, axis=0)} microns")
    
    # Convert vertices from microns to voxel indices for boundary analysis
    voxel_indices = np.round(np.array(vertices) / np.array(voxel_size)).astype(int)
    out_of_bounds = (
        (voxel_indices[:, 0] < 0) | (voxel_indices[:, 0] >= grid_shape[0]) |
        (voxel_indices[:, 1] < 0) | (voxel_indices[:, 1] >= grid_shape[1]) |
        (voxel_indices[:, 2] < 0) | (voxel_indices[:, 2] >= grid_shape[2])
    )
    if np.any(out_of_bounds):
        print(f"Warning: {np.sum(out_of_bounds)} vertices are outside image bounds and will be clamped to boundaries")
    
    if radius is not None:
        chunks = np.array_split(vertices, num_workers)
        with Pool(num_workers) as pool:
            results = []
            progress_queue = multiprocessing.Manager().Queue()
            for i, result in enumerate(pool.imap_unordered(process_chunk, [(chunk, radius, grid_shape, voxel_size, progress_queue) for chunk in chunks])):
                results.append(result)
                print_progress(i + 1, len(chunks))
            mesh = np.zeros(grid_shape, dtype=bool)
            for result in results:
                mesh |= result
    else:
        mesh = np.zeros(grid_shape, dtype=bool)
        
        # Clamp indices to valid bounds (fill up to boundary for out-of-bounds vertices)
        clamped_indices = np.clip(voxel_indices, 0, np.array(grid_shape) - 1)
        
        # Set voxels for all vertices (clamped to boundaries)
        if len(clamped_indices) > 0:
            mesh[tuple(clamped_indices.T)] = True
        
        print(f"Processed {len(vertices)} vertices (clamped out-of-bounds to image boundaries)")
    
    # Flip the mesh along the X and Y axes to correct the origin
    mesh = np.flip(mesh, axis=(0, 1))
    matrix = mesh.astype(np.uint8) * 255
    
    # Create header with template properties if available, otherwise use defaults
    header = {
        'encoding': 'gzip',
        'space': template_header.get('space', 'right-anterior-superior'),
        'space directions': template_header.get('space directions', [(voxel_size[0], 0, 0), (0, voxel_size[1], 0), (0, 0, voxel_size[2])]),
        'space units': template_header.get('space units', ['microns', 'microns', 'microns']),
        'kinds': template_header.get('kinds', ['domain', 'domain', 'domain'])
    }
    
    # Add space origin if it was in the template
    if 'space origin' in template_header:
        header['space origin'] = template_header['space origin']
    
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
        print("Usage: python obj_to_nrrd.py input.obj [output.nrrd] ['(X,Y,Z)'] [radius] ['(voxel_size_x, voxel_size_y, voxel_size_z)'] [template.nrrd]")
        print("  OR: python obj_to_nrrd.py input.obj template.nrrd output.nrrd [radius]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = None
    extent = None
    radius = None
    voxel_size = None
    template_file = None

    # Check if second argument is a template file (ends with .nrrd and exists)
    if len(sys.argv) > 2 and sys.argv[2].endswith('.nrrd') and os.path.exists(sys.argv[2]):
        # New format: input.obj template.nrrd output.nrrd [radius]
        template_file = sys.argv[2]
        if len(sys.argv) > 3:
            output_file = sys.argv[3]
        if len(sys.argv) > 4:
            radius = float(sys.argv[4])
        print(f"Using template mode: template={template_file}, output={output_file}")
    else:
        # Original format: input.obj [output.nrrd] ['(X,Y,Z)'] [radius] ['(voxel_size_x, voxel_size_y, voxel_size_z)'] [template.nrrd]
        if len(sys.argv) > 2:
            # Check if it's a template file path at the end
            if sys.argv[-1].endswith('.nrrd') and os.path.exists(sys.argv[-1]) and len(sys.argv) > 2:
                template_file = sys.argv[-1]
                # Remove template from processing other args
                args_without_template = sys.argv[:-1]
            else:
                args_without_template = sys.argv
            
            # Process remaining arguments in original order
            if len(args_without_template) > 2:
                output_file = args_without_template[2]

            if len(args_without_template) > 3:
                extent = args_without_template[3]
                extent = tuple(map(int, extent.strip("()").split(",")))

            if len(args_without_template) > 4:
                radius = float(args_without_template[4])

            if len(args_without_template) > 5:
                voxel_size = args_without_template[5]
                voxel_size = tuple(map(float, voxel_size.strip("()").split(",")))

    obj_to_nrrd(input_file, output_file=output_file, extent=extent, voxel_size=voxel_size, radius=radius, num_workers=5, template_file=template_file)
