import argparse
from PIL import Image

def make_transparent(input_file, output_file):
    with Image.open(input_file) as im:
        # Convert the image to RGBA mode
        im = im.convert("RGBA")
        # Get the color of the top-left pixel
        bg_color = im.getpixel((0, 0))
        # Make all pixels with the same color as the top-left pixel transparent
        data = im.getdata()
        new_data = []
        for item in data:
            if item[:3] == bg_color:
                new_data.append((0, 0, 0, 0))
            else:
                new_data.append(item)
        im.putdata(new_data)
        # Save the transparent image
        im.save(output_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='Input PNG file')
    parser.add_argument('output', help='Output PNG file')
    args = parser.parse_args()
    make_transparent(args.input, args.output)
