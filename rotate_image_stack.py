import numpy as np
import nrrd

def rotate_image_stack(data, voxel_size):
    print(f"Voxel size: {voxel_size}")
    
    print(f"Data size: {np.shape(data)}")
    
    axis_lengths = np.array(data.shape) * voxel_size
    
    # Determine the longest axis and the next longest axis
    longest_axis, next_axis = np.argsort(axis_lengths)[::-1][:2]
    print(f"Axis lengths: {axis_lengths}")
    print(f"Longest axis: {longest_axis}")
    print(f"Next axis: {next_axis}")

    if axis_lengths[longest_axis] != axis_lengths[next_axis]:
        # Determine the number of rotations required to align the longest axis with the X axis
        num_rotations = (3 - longest_axis) % 3

        print(f"Number of rotations: {num_rotations}")

        # Rotate the data and the voxel size accordingly
        for _ in range(num_rotations):
            print("90 degree rotation")
            data = np.rot90(data, axes=(0, 1))
            voxel_size = list(voxel_size)
            voxel_size[0], voxel_size[1] = voxel_size[1], voxel_size[0]
            voxel_size = tuple(voxel_size)
            print(f"Voxel size: {voxel_size}")
            print(f"Data size: {np.shape(data)}")
        
        # Determine the number of rotations required to align the next longest axis with the Y axis
        num_rotations = (next_axis - 1) % 3

        print(f"Number of rotations: {num_rotations}")

        # Rotate the data and the voxel size accordingly
        for _ in range(num_rotations):
            print("90 degree rotation")
            data = np.rot90(data, axes=(1, 2))
            voxel_size = list(voxel_size)
            voxel_size[1], voxel_size[2] = voxel_size[2], voxel_size[1]
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
