import numpy as np
import nrrd

def rotate_image_stack(data, voxel_size):
    print(f"Voxel size: {voxel_size}")
    
    print(f"Data size: {np.shape(data)}")
    
    # Determine the longest axis and the next longest axis
    axis_lengths = np.array(data.shape) * voxel_size

    print(f"Axis lengths: {axis_lengths}")
    
    longest_axis, next_axis = np.argsort(axis_lengths)[::-1][:2]
    
    print(f"Longest axis: {longest_axis}")
    print(f"Next axis: {next_axis}")

    # Determine the number of rotations required to align the longest axis with the X axis
    num_rotations = (longest_axis - 1) % 3
    
    print(f"Number of rotations: {num_rotations}")

    # Rotate the data and the voxel size accordingly
    for _ in range(num_rotations):
        print("90 degree rotation")
        data = np.rot90(data, axes=(1, 0))
        voxel_size = (voxel_size[1],voxel_size[0],voxel_size[2])
        print(f"Voxel size: {voxel_size}")
        print(f"Data size: {np.shape(data)}")

    # Determine the axis permutation required to put the next longest axis in the Y axis
    axis_permutation = [2, 0, 1] if next_axis == 0 else [1, 0, 2]
    
    print("transpose")
    # Permute the axes of the data and the voxel size accordingly
    data = np.transpose(data, axis_permutation)
    voxel_size = voxel_size[axis_permutation]

    print(f"Voxel size: {voxel_size}")
    print(f"Data size: {np.shape(data)}")
    
    print("flip")
    
    # Flip the data array along the Z axis
    data = np.flip(data, axis=0)
    
    print(f"Voxel size: {voxel_size}")
    print(f"Data size: {np.shape(data)}")
    
    return data, voxel_size


# # Load NRRD file
# data, header = nrrd.read('/path/to/image_stack.nrrd')
# voxel_size = np.sqrt(np.sum(np.square(header['space directions']), axis=1))

# # Rotate the image stack
# data, voxel_size = rotate_image_stack(data, voxel_size)
