import argparse
from PIL import Image

def merge_images(input_path1, input_path2, output_path):
    # Open the input images
    img1 = Image.open(input_path1).convert('RGBA')
    img2 = Image.open(input_path2).convert('RGBA')

    # Ensure both images have the same size
    if img1.size != img2.size:
        raise ValueError('Input images must have the same size')

    # Make the first image semi-transparent
    img1.putalpha(40)

    # Merge the images
    result = Image.alpha_composite(img2, img1)

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
