import argparse
import numpy as np
from PIL import Image


def grayscale_image(input_path, output_path):
    # Load input image
    input_image = Image.open(input_path)

    # Convert to grayscale using luminosity method
    grayscale_image = input_image.convert('L')

    # Save grayscale image
    grayscale_image.save(output_path)


if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Convert a PNG image to grayscale.')
    parser.add_argument('input_path', help='path to input PNG image')
    parser.add_argument('output_path', help='path to save grayscale PNG image')
    args = parser.parse_args()

    # Convert input image to grayscale
    grayscale_image(args.input_path, args.output_path)
