import numpy as np
import nrrd
from PIL import Image
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
import argparse

def colorize_image_stack(nrrd_path, png_path, thumbnail=False):
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
    depth, height, width = data.shape

    # Replace any NaN or inf values with zeros
    data = np.nan_to_num(data)

    # Find first and last non-zero Z indices
    first_index = np.argmax((data > 0).any(axis=(1, 2)))
    last_index = data.shape[0] - np.argmax((data > 0)[::-1].any(axis=(1, 2))) - 1

    print('First non-zero Z index:', first_index)
    print('Last non-zero Z index:', last_index)

    # Calculate maximum intensity projection across Z
    mip = np.max(data, axis=0)

    # Find indices of maximum values for each X,Y position offset by first_index
    max_indices = np.argmax(data, axis=0) - first_index
    max_indices = np.clip(max_indices, 0, None)

    # Define color map using JET color scheme
    jet_cmap = plt.cm.get_cmap('jet')
    colors = jet_cmap(np.linspace(0, 1, last_index - first_index + 1))
    colors = np.vstack(([0, 0, 0, 1], colors)) # add black at index 0
    cmap = ListedColormap(colors)

    # Create an empty array to store the colorized image
    colorized_image = np.zeros((height, width, 3), dtype=np.uint8)

    # Loop through each X,Y position and set the color based on the max Z value
    for y in range(height):
        for x in range(width):
            index = max_indices[y, x]
            colorized_image[y, x, :] = np.uint8(np.multiply(cmap(index)[0:3],mip[y, x]))

    # Save the colorized image as a PNG file
    if thumbnail:
        Image.fromarray(colorized_image).resize((256, 256), resample=Image.Resampling.BILINEAR).save(png_path)
    else:
        Image.fromarray(colorized_image).save(png_path)

if __name__ == '__main__':
    # Define command line arguments
    parser = argparse.ArgumentParser(description='Create a color depth MIP from an NRRD image stack.')
    parser.add_argument('--nrrd', type=str, help='Path to the NRRD image stack')
    parser.add_argument('--png', type=str, help='Path to save the resulting PNG file')
    parser.add_argument('--thumb', type=bool, help='wheather to reduce the size of the resulting PNG file', default=False)

    # Parse command line arguments
    args = parser.parse_args()

    # Call function to create color depth MIP
    colorize_image_stack(args.nrrd, args.png, args.thumb)
