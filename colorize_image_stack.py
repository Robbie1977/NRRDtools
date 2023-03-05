import numpy as np
import nrrd
from PIL import Image
from matplotlib.colors import ListedColormap
import argparse

def colorize_image_stack(input_file, output_file):
    # Load NRRD file
    data, header = nrrd.read(input_file)
    depth = data.shape[0]

    # Replace any NaN or inf values with zeros
    data = np.nan_to_num(data)

    # Calculate maximin intensity projection
    mip = np.max(data, axis=0) - np.min(data, axis=0)

    # Normalize mip
    mip_norm = (mip - np.min(mip)) / (np.max(mip) - np.min(mip))

    # Create color map using Janelia color scheme
    colors = [[0.00, 0.00, 0.00], [0.00, 0.00, 0.75], [0.00, 0.50, 1.00], [0.00, 0.75, 0.50], [1.00, 0.75, 0.00], [1.00, 0.25, 0.00], [0.75, 0.00, 0.00], [0.75, 0.00, 0.75], [0.75, 0.75, 0.75]]
    cmap = ListedColormap(colors)

    # Create an empty list to store colorized images
    colorized_images = []

    # Loop through the stack and apply color as a filter on each image
    for i in range(depth):
        # Normalize data to 0-255 range
        data_norm = (data[i] - np.min(data[i])) / (np.max(data[i]) - np.min(data[i])) * 255

        # Create color map for the layer using rainbow color scheme
        layer_colors = np.array([cmap(j) for j in np.linspace(0, 1, 256)])
        layer_cmap = ListedColormap(layer_colors)

        # Apply layer color as a filter
        layer_rgb = layer_cmap(data_norm)[:,:,:3]

        # Resize the colorized layer to match the size of the mip
        layer_rgb_resized = np.array(Image.fromarray(np.uint8(layer_rgb)).resize((mip.shape[1], mip.shape[0])))

        # Add colorized layer to the list of colorized images
        colorized_images.append(layer_rgb_resized)

    # Merge colorized layers using maximum intensity projection
    mip_colorized = np.max(np.array(colorized_images), axis=0)

    # Normalize the merged image to 0-255 range
    mip_colorized_norm = (mip_colorized - np.min(mip_colorized)) / (np.max(mip_colorized) - np.min(mip_colorized)) * 255

    # Convert normalized merged image to RGB image using color map
    mip_colorized_rgb = cmap(mip_colorized_norm)[:,:,:3]

    # Create thumbnail
    thumbnail = Image.fromarray(np.uint8(mip_colorized_rgb))
    thumbnail = thumbnail.resize((256, 256))

    # Save thumbnail
    thumbnail.save(output_file)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Colorize an image stack.')
    parser.add_argument('input_file', type=str, help='Path to input NRRD file')
    parser.add_argument('output_file', type=str, help='Path to output colorized thumbnail file')
    args = parser.parse_args()

