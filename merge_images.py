import argparse
import numpy as np
from PIL import Image

def merge_images(input_path1, input_path2, output_path):
    # Open the input images
    img1 = Image.open(input_path1).convert('RGBA')
    img2 = Image.open(input_path2).convert('RGBA')

    # Allow for a 2 pixel colour bar on right:
    color_bar_width = 2
    if img2.size[1] == img1.size[1] and img2.size[0] - img1.size[0] == color_bar_width:
        color_bar_height = img1.size[1]
        color_bar = np.zeros((color_bar_height, color_bar_width, 4), dtype=np.uint8)
        img1 = Image.fromarray(np.concatenate((np.array(img1), color_bar), axis=1))
    
    # Ensure both images have the same size
    if img1.size != img2.size:
        print(f"Template size: {img1.size}")
        print(f"Signal size: {img2.size}")
        raise ValueError('Input images must have the same size')

    # Make the first image semi-transparent
    img1.putalpha(40)

    # Merge the images
    result = Image.alpha_composite(img1, img2)

    # Save the result image
    result.save(output_path)

if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Merge two PNG images')
    parser.add_argument('input1', type=str, help='path to the template image')
    parser.add_argument('input2', type=str, help='path to the signal image')
    parser.add_argument('output', type=str, help='path to the output image')
    args = parser.parse_args()

    # Merge the images
    merge_images(args.input1, args.input2, args.output)
