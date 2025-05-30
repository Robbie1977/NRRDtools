import argparse
import numpy as np
import nrrd
from PIL import Image
from rotate_image_stack import rotate_image_stack


def create_mip(nrrd_path, png_path, thumb=False, add_colorbar_padding=False):
    # Load NRRD file
    data, header = nrrd.read(nrrd_path)
    
    directions = header['space directions']
    
    # Calculate voxel sizes from direction cosines
    voxel_sizes = tuple(np.sqrt(np.sum(np.square(directions), axis=1)))
    
    # Rotate image stack
    data, voxel_sizes = rotate_image_stack(data, voxel_sizes)
    height, width, depth = data.shape
    
    # Calculate maximum intensity projection across Z
    mip = np.max(data, axis=2)
    # Calculate physical dimensions of MIP
    x_size, y_size = np.multiply(voxel_sizes[:2], [width, height])
    # Calculate ratio of physical dimensions
    ratio = y_size / x_size
    # Create thumbnail image by resizing the MIP while preserving aspect ratio
    thumbnail = Image.fromarray(mip)
    if thumb:
        print(f"Reducing images size from: {height} x {width}")
        thumbnail_width = 256
        thumbnail_height = int(thumbnail_width * ratio)
        thumbnail = thumbnail.resize((thumbnail_width, thumbnail_height))
    thumbnail = thumbnail.rotate(-90, expand=True)
    
    # Get original image size
    width, height = thumbnail.size
    print(f"Original thumbnail size: {width} x {height}")
    
    if add_colorbar_padding:
        # Create a new image with 2 extra pixels width and copy the original into it
        padded_width = width + 2
        padded = Image.new('L', (padded_width, height), 0)  # 'L' for grayscale, 0 for black
        padded.paste(thumbnail, (0, 0))  # Paste at left edge
        print(f"Padded thumbnail size: {padded_width} x {height}")
        thumbnail = padded
    
    # Save the thumbnail image as a PNG file
    thumbnail.save(png_path)

if __name__ == '__main__':
    # Create argument parser
    parser = argparse.ArgumentParser(description='Create maximum intensity projection (MIP) from an image stack NRRD and save [a thumbnail] as a PNG file.')
    # Define arguments
    parser.add_argument('nrrd_path', type=str, help='Path to image stack NRRD file')
    parser.add_argument('png_path', type=str, help='Path to output PNG file')
    parser.add_argument('--thumb', action='store_true', help='Reduce size to thumbnail')
    parser.add_argument('--add_colorbar_padding', action='store_true', 
                       help='Add 2 pixels of padding for colorbar alignment')
    # Parse arguments
    args = parser.parse_args()
    # Create MIP and save thumbnail as PNG file
    create_mip(args.nrrd_path, args.png_path, args.thumb, args.add_colorbar_padding)
