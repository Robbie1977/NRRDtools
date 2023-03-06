import argparse
import numpy as np
import nrrd
from PIL import Image

def create_mip(nrrd_path, png_path):
    # Load NRRD file
    data, header = nrrd.read(nrrd_path)
    depth, height, width = data.shape

    # Calculate maximum intensity projection across Z
    mip = np.max(data, axis=0)

    # Create thumbnail image by resizing the MIP to 256x256
    thumbnail = Image.fromarray(mip).resize((256, 256))

    # Save the thumbnail image as a PNG file
    thumbnail.save(png_path)

if __name__ == '__main__':
    # Create argument parser
    parser = argparse.ArgumentParser(description='Create maximum intensity projection (MIP) from an image stack NRRD and save a thumbnail as a PNG file.')

    # Define arguments
    parser.add_argument('nrrd_path', type=str, help='Path to image stack NRRD file')
    parser.add_argument('png_path', type=str, help='Path to output PNG file')

    # Parse arguments
    args = parser.parse_args()

    # Create MIP and save thumbnail as PNG file
    create_mip(args.nrrd_path, args.png_path)
