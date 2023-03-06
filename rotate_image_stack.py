import numpy as np
import nrrd

def rotate_image_stack(data, voxel_size):
    # Determine the longest axis and the next longest axis
    axis_lengths = np.array(data.shape) * voxel_size
    longest_axis, next_axis = np.argsort(axis_lengths)[::-1][:2]

    # Determine the number of rotations required to align the longest axis with the Y axis
    num_rotations = (longest_axis - 2) % 3

    # Rotate the data and the voxel size accordingly
    for _ in range(num_rotations):
        data = np.rot90(data, axes=(2, 1))
        voxel_size = np.roll(voxel_size, 1)

    # Determine the axis permutation required to put the next longest axis in the X axis
    axis_permutation = [1, 2, 0] if next_axis == 0 else [0, 2, 1]

    # Permute the axes of the data and the voxel size accordingly
    data = np.transpose(data, axis_permutation)
    voxel_size = voxel_size[axis_permutation]

    return data, voxel_size


# # Load NRRD file
# data, header = nrrd.read('/path/to/image_stack.nrrd')
# voxel_size = np.sqrt(np.sum(np.square(header['space directions']), axis=1))

# # Rotate the image stack
# data, voxel_size = rotate_image_stack(data, voxel_size)