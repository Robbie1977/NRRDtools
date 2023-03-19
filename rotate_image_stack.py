import numpy as np
import nrrd
from scipy.ndimage import zoom

def resample_to_isotropic(data, voxel_size):
    target_voxel_size = min(voxel_size)
    resample_factors = voxel_size / target_voxel_size
    isotropic_data = zoom(data, resample_factors, order=1)  # Using bilinear interpolation (order=1)
    isotropic_voxel_size = np.array([target_voxel_size] * 3)
    
    return isotropic_data, isotropic_voxel_size

def rotate_image_stack(data, voxel_size):
    print(f"Original voxel size: {voxel_size}")
    print(f"Original data size: {np.shape(data)}")

    # Resample the data to isotropic voxels
    data, voxel_size = resample_to_isotropic(data, voxel_size)
    print(f"Isotropic voxel size: {voxel_size}")
    print(f"Isotropic data size: {np.shape(data)}")
    
    axis_lengths = np.array(data.shape) * voxel_size
    
    # Determine the longest axis, the next longest axis, and the shortest axis
    sorted_indices = np.argsort(axis_lengths)[::-1]
    longest_axis, next_axis, shortest_axis = sorted_indices[0], sorted_indices[1], sorted_indices[2]
    print(f"Axis lengths: {axis_lengths}")
    print(f"Longest axis: {longest_axis}")
    print(f"Next axis: {next_axis}")
    print(f"Shortest axis: {shortest_axis}")

    if axis_lengths[longest_axis] != axis_lengths[next_axis] and next_axis != 2:
        # Swap the longest axis with the X axis
        print("Swapping longest axis with X axis")
        data = np.swapaxes(data, 0, longest_axis)
        voxel_size = list(voxel_size)
        voxel_size[0], voxel_size[longest_axis] = voxel_size[longest_axis], voxel_size[0]
        if next_axis == 0:
            next_axis = longest_axis
        voxel_size = tuple(voxel_size)
        print(f"Voxel size: {voxel_size}")
        print(f"Data size: {np.shape(data)}")

        # Swap the shortest axis with the Y axis
        print("Swapping shortest axis with Y axis")
        data = np.swapaxes(data, 1, next_axis)
        voxel_size = list(voxel_size)
        voxel_size[1], voxel_size[next_axis] = voxel_size[next_axis], voxel_size[1]
        voxel_size = tuple(voxel_size)
        print(f"Voxel size: {voxel_size}")
        print(f"Data size: {np.shape(data)}")

    print(f"Voxel size: {voxel_size}")
    print(f"Data size: {np.shape(data)}")
    
    return data, voxel_size

# Load NRRD file
# data, header = nrrd.read('/path/to/image_stack.nrrd')
# voxel_size = np.sqrt(np.sum(np.square(header['space directions']), axis=1))

# Rotate the image stack
# data, voxel_size = rotate_image_stack(data, voxel_size)
