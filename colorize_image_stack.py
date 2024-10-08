import numpy as np
import nrrd
from PIL import Image
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
import argparse
from rotate_image_stack import rotate_image_stack

def colorize_image_stack(nrrd_path, png_path, thumbnail=False, add_scale=True, max_scale=False):
    '''
    Load an NRRD image stack and create a color depth MIP by setting the color of each pixel based on the
    Z index with the maximum voxel intensity at that position, using a JET color scale. The resulting image
    is saved as a PNG file.
    
    Arguments:
    nrrd_path -- path to the NRRD image stack
    png_path -- path to save the resulting PNG file
    
    Example usage:
    python colorize_image_stack.py --nrrd /path/to/image_stack.nrrd --png /path/to/output.png
    '''
    # Load NRRD file
    data, header = nrrd.read(nrrd_path)
    voxel_size = np.sqrt(np.sum(np.square(header['space directions']), axis=1))
    data, voxel_size = rotate_image_stack(data, voxel_size)
    width, height, depth = data.shape

    # Replace any NaN or inf values with zeros
    data = np.nan_to_num(data)

    # Find first and last non-zero Z indices
    first_index = np.argmax((data > 0)[:, :, ::1].any(axis=(0, 1)))
    last_index = data.shape[2] - np.argmax((data > 0)[:, :, ::-1].any(axis=(0, 1))) - 1

    print('First non-zero Z index:', first_index)
    print('Last non-zero Z index:', last_index)
    
    if first_index > last_index:
        print('index error - reversing')
        first_index, last_index = [last_index, first_index]
        
    if max_scale:
        print('Extending scale to full stack')
        first_index = 0
        last_index = data.shape[2] - 1

    # Calculate maximum intensity projection across Z
    mip = np.max(data, axis=2)

    # Find indices of maximum values for each X,Y position offset by first_index
    max_indices = np.argmax(data, axis=2) - first_index
    max_indices = np.clip(max_indices, 0, None)

    # Define color map using JET color scheme
    jet_cmap = plt.get_cmap('jet')
    colors = jet_cmap(np.linspace(0, 1, last_index - first_index + 1))
    colors = np.vstack(([0, 0, 0, 1], colors)) # add black at index 0
    cmap = ListedColormap(colors)

    # Create an empty array to store the colorized image
    colorized_image = np.zeros((width, height, 3), dtype=np.uint8)

    print(np.shape(max_indices))
    print(np.shape(mip))
    print(np.shape(colorized_image))
    
    # Loop through each X,Y position and set the color based on the max Z value
    for y in range(width):
        for x in range(height):
            index = max_indices[y, x]
            colorized_image[y, x, :] = np.uint8(np.multiply(cmap(index)[0:3],mip[y, x]))
    
    # Rotate clockwise to make wider than longer
    colorized_image = np.rot90(colorized_image, -1)
    height, width, rgb = colorized_image.shape
    
    if add_scale:
        print('Add color bar to the right of the image')
        # Add color bar to the right side of the image
        color_bar_width = 2
        color_bar_height = height
        color_bar = np.zeros((color_bar_height, color_bar_width, 3), dtype=np.uint8)
        for y in range(color_bar_height):
            index = int((y / height) * depth) - first_index
            if index >= 0 and index <= last_index - first_index:
                color_bar[y, :, :] = np.uint8(np.multiply(cmap(index)[0:3], 255))
        
        # Combine colorized image and color bar
        combined_image = np.concatenate((colorized_image, color_bar), axis=1)

    # Save the colorized image as a PNG file
    if thumbnail:
        # Calculate physical dimensions of MIP
        y_size, x_size = np.multiply(voxel_size[:2], [width, height])
        
        # Calculate ratio of physical dimensions
        ratio = y_size / x_size
        
        # Create thumbnail image by resizing the MIP while preserving aspect ratio
        if add_scale:
            thumbnail = Image.fromarray(combined_image)
        else:
            thumbnail = Image.fromarray(colorized_image)
        thumbnail_width = 256
        thumbnail_height = int(thumbnail_width * ratio)
        thumbnail = thumbnail.resize((thumbnail_width, thumbnail_height))
        # Save the thumbnail image as a PNG file
        thumbnail.save(png_path)
    else:
        if add_scale:
            Image.fromarray(combined_image).save(png_path)
        else:
            Image.fromarray(colorized_image).save(png_path)
        

if __name__ == '__main__':
    # Define command line arguments
    parser = argparse.ArgumentParser(description='Create a color depth MIP from an NRRD image stack.')
    parser.add_argument('--nrrd', type=str, help='Path to the NRRD image stack')
    parser.add_argument('--png', type=str, help='Path to save the resulting PNG file')
    parser.add_argument('--thumb', action='store_true', help='Reduce size to thumbnail')
    parser.add_argument('--scale', action='store_true', help='Add colour scale bar to thumbnail')
    parser.add_argument('--max', action='store_true', help='Max colour scale bar to full Z range')

    # Parse command line arguments
    args = parser.parse_args()

    # Call function to create color depth MIP
    colorize_image_stack(args.nrrd, args.png, args.thumb, args.scale, args.max)
