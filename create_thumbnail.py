import argparse
import os
import random

def create_thumbnail(template_file, signal_file, output_file, cache_template=False):
    # Set up paths to the necessary files
    merge_images_path = os.path.join(os.getcwd(), "merge_images.py")
    colorize_image_stack_path = os.path.join(os.getcwd(), "colorize_image_stack.py")
    create_mip_path = os.path.join(os.getcwd(), "create_mip.py")
    
    # Generate a random number for temporary file names
    rand_num = str(random.randint(1000, 9999))
    
    if cache_template:
        # extract the template id from the VFB specific folder structure
        template_id = parent_dir = os.path.basename(os.path.dirname(template_file))
        template_mip = f"template_mip_{template_id}.png"
    else:
        template_mip = "template_mip_{rand_num}.png"
   
    # Create the maximum intensity projection of the template
    if not cache_template or not os.path.exists(template_mip): 
        os.system(f"python3 {create_mip_path} {template_file} {template_mip}")
    
    # Colorize the signal image
    os.system(f"python3 {colorize_image_stack_path} --nrrd {signal_file} --png signal_colorized_{rand_num}.png --scale")
    
    # Merge the template and colorized signal images
    os.system(f"python3 {merge_images_path} {template_mip} signal_colorized_{rand_num}.png {output_file}")
    
    # Clean up temporary files
    if not cache_template:
        os.remove(f"{template_mip}")
    os.remove(f"signal_colorized_{rand_num}.png")

def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description="Create a thumbnail image from a Template.nrrd file and a Signal.nrrd file.")
    
    # Add arguments
    parser.add_argument("template_file", help="Path to Template.nrrd file")
    parser.add_argument("signal_file", help="Path to Signal.nrrd file")
    parser.add_argument("output_file", help="Path to output thumbnail.png file")
    parser.add_argument('--cache', action='store_true', help='If added then the template mips are cached')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create thumbnail
    create_thumbnail(args.template_file, args.signal_file, args.output_file, args.cache)

if __name__ == "__main__":
    main()
