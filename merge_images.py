import argparse
import numpy as np
from PIL import Image
import os

def merge_images(input_path1, input_path2, output_path):
    # Check if input files exist
    if not os.path.exists(input_path1):
        raise FileNotFoundError(f"Background image not found: {input_path1}")
    if not os.path.exists(input_path2):
        raise FileNotFoundError(f"Signal image not found: {input_path2}")
        
    # Open the input images
    try:
        img1 = Image.open(input_path1).convert('RGBA')
    except Exception as e:
        raise RuntimeError(f"Failed to open background image {input_path1}: {str(e)}")
        
    try:
        img2 = Image.open(input_path2).convert('RGBA')
    except Exception as e:
        raise RuntimeError(f"Failed to open signal image {input_path2}: {str(e)}")

    # Allow for a 2 pixel colour bar on right:
    color_bar_width = 2
    if img2.size[1] == img1.size[1] and img2.size[0] - img1.size[0] == color_bar_width:
        color_bar_height = img1.size[1]
        color_bar = np.zeros((color_bar_height, color_bar_width, 4), dtype=np.uint8)
        img1 = Image.fromarray(np.concatenate((np.array(img1), color_bar), axis=1))
    
    # Ensure both images have the same size
    if img1.size != img2.size:
        raise ValueError(f'Input images must have the same size. Background: {img1.size}, Signal: {img2.size}')

    # Make the first image semi-transparent
    img1.putalpha(40)
    
    # Set signal alpha to max RGB
    sig_arr = np.array(img2)
    sig_arr[..., 3] = np.max(sig_arr[..., :3], axis=2)
    img2 = Image.fromarray(sig_arr)
    
    # Merge the images
    result = Image.alpha_composite(img2, img1)
    result.putalpha(255)
    
    # Save the result image
    try:
        result.save(output_path)
        
        # Set file permissions to 777
        os.chmod(output_path, 0o777)
        
        # Verify output size matches
        output_img = Image.open(output_path)
        if output_img.size != img2.size:
            raise RuntimeError(f"Output image size {output_img.size} does not match input size {img2.size}")
        
        print(f"Successfully merged:")
        print(f"  Background: {input_path1} ({img1.size})")
        print(f"  Signal: {input_path2} ({img2.size})")
        print(f"  Output: {output_path} ({output_img.size})")
    except Exception as e:
        raise RuntimeError(f"Failed to save or verify merged image to {output_path}: {str(e)}")

if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Merge two PNG images')
    parser.add_argument('input1', type=str, help='path to the template image')
    parser.add_argument('input2', type=str, help='path to the signal image')
    parser.add_argument('output', type=str, help='path to the output image')
    args = parser.parse_args()
    
    try:
        # Merge the images
        merge_images(args.input1, args.input2, args.output)
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)
