#!/usr/bin/env python3
import argparse
import os
import random
import sys
import logging

def setup_logging():
    """Configure logging for the script."""
    logger = logging.getLogger("CreateThumbnail")
    logger.setLevel(logging.DEBUG)

    # Create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Create file handler for detailed logs
    fh = logging.FileHandler("create_thumbnail.log")
    fh.setLevel(logging.DEBUG)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger

def execute_python_script(script_path, args, logger):
    """
    Execute a Python script by directly calling its main function.
    
    Parameters:
        script_path (str): Path to the Python script
        args (list): List of arguments to pass to the script
        logger (logging.Logger): Logger instance for logging messages
        
    Returns:
        bool: True if execution succeeds, False otherwise
    """
    logger.debug(f"Executing script: {script_path} with args: {args}")

    try:
        # Add script directory to path if needed
        script_dir = os.path.dirname(os.path.abspath(script_path))
        if script_dir not in sys.path:
            sys.path.append(script_dir)

        # Import the script module
        script_name = os.path.splitext(os.path.basename(script_path))[0]
        module = __import__(script_name)

        # Handle different script types
        if script_name == 'create_mip':
            # Extract args for create_mip.py
            parser = argparse.ArgumentParser()
            parser.add_argument('nrrd_path', type=str)
            parser.add_argument('png_path', type=str)
            parser.add_argument('--thumb', action='store_true')
            parser.add_argument('--add_colorbar_padding', action='store_true')
            parsed_args = parser.parse_args(args)
            
            module.create_mip(
                parsed_args.nrrd_path, 
                parsed_args.png_path,
                parsed_args.thumb,
                parsed_args.add_colorbar_padding
            )
            return True
            
        elif script_name == 'colorize_image_stack':
            # Extract args for colorize_image_stack.py
            parser = argparse.ArgumentParser()
            parser.add_argument('--nrrd', type=str)
            parser.add_argument('--png', type=str)
            parser.add_argument('--thumb', action='store_true')
            parser.add_argument('--scale', action='store_true')
            parser.add_argument('--max', action='store_true')
            parsed_args = parser.parse_args(args)
            
            module.colorize_image_stack(
                parsed_args.nrrd,
                parsed_args.png,
                parsed_args.thumb,
                parsed_args.scale,
                parsed_args.max
            )
            return True

        elif script_name == 'merge_images':
            # Extract args for merge_images.py
            parser = argparse.ArgumentParser()
            parser.add_argument('input1', type=str)
            parser.add_argument('input2', type=str)
            parser.add_argument('output', type=str)
            parsed_args = parser.parse_args(args)
            
            module.merge_images(
                parsed_args.input1,
                parsed_args.input2,
                parsed_args.output
            )
            return True

        # For other scripts with main()
        elif hasattr(module, 'main'):
            sys.argv = [script_path] + args
            module.main()
            return True

        logger.error(f"No suitable entry point found in {script_path}")
        return False

    except Exception as e:
        logger.error(f"Failed to execute {script_path}: {str(e)}")
        return False

def create_thumbnail(template_file, signal_file, output_file, cache_template=False, max_scale=False, add_colorbar_padding=True, logger=None):
    """
    Create a thumbnail by processing template and signal NRRD files.

    Parameters:
        template_file (str): Path to the Template.nrrd file.
        signal_file (str): Path to the Signal.nrrd file.
        output_file (str): Path to the output thumbnail.png file.
        cache_template (bool): Whether to cache template MIPs.
        max_scale (bool): Whether to use max scale for colorization.
        add_colorbar_padding (bool): Whether to add padding for colorbar alignment.
        logger (logging.Logger): Logger instance for logging messages.
    """
    if logger is None:
        logger = logging.getLogger("CreateThumbnail")

    # Verify input files exist
    if not os.path.isfile(template_file):
        logger.error(f"Template file does not exist: {template_file}")
        sys.exit(1)
    if not os.path.isfile(signal_file):
        logger.error(f"Signal file does not exist: {signal_file}")
        sys.exit(1)

    # Set up paths to the necessary scripts
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    merge_images_path = os.path.join(scripts_dir, "merge_images.py")
    colorize_image_stack_path = os.path.join(scripts_dir, "colorize_image_stack.py")
    create_mip_path = os.path.join(scripts_dir, "create_mip.py")

    # Verify that the scripts exist
    for script in [merge_images_path, colorize_image_stack_path, create_mip_path]:
        if not os.path.isfile(script):
            logger.error(f"Required script not found: {script}")
            sys.exit(1)

    # Generate a random number for temporary file names
    rand_num = str(random.randint(1000, 9999))

    # Determine the template MIP file name
    if cache_template:
        template_id = os.path.basename(os.path.dirname(template_file))
        template_mip = f"template_mip_{template_id}.png"
    else:
        template_mip = f"template_mip_{rand_num}.png"

    # Create the maximum intensity projection of the template
    if not cache_template or not os.path.exists(template_mip):
        logger.info(f"Creating MIP for template: {template_file} -> {template_mip}")
        mip_args = [template_file, template_mip]
        if add_colorbar_padding:
            mip_args.append("--add_colorbar_padding")
        if not execute_python_script(create_mip_path, mip_args, logger):
            logger.error("Failed to create template MIP.")
            sys.exit(1)
    else:
        logger.info(f"Using cached template MIP: {template_mip}")

    # Colorize the signal image
    signal_colorized = f"signal_colorized_{rand_num}.png"
    colorize_args = [
        "--nrrd", signal_file,
        "--png", signal_colorized,
        "--scale"
    ]
    if max_scale:
        logger.info("Producing with max scale...")
        colorize_args.append("--max")
    
    if not execute_python_script(colorize_image_stack_path, colorize_args, logger):
        logger.error("Failed to colorize signal image.")
        # Clean up and exit
        if not cache_template and os.path.exists(template_mip):
            os.remove(template_mip)
            logger.debug(f"Removed temporary file: {template_mip}")
        sys.exit(1)

    # Execute merge images script
    merge_args = [template_mip, signal_colorized, output_file]
    if not execute_python_script(merge_images_path, merge_args, logger):
        logger.error("Failed to merge images.")
        sys.exit(1)

    # Clean up temporary files
    try:
        if false and not cache_template and os.path.exists(template_mip):
            os.remove(template_mip)
            logger.debug(f"Removed temporary file: {template_mip}")
        if false and os.path.exists(signal_colorized):
            os.remove(signal_colorized)
            logger.debug(f"Removed temporary file: {signal_colorized}")
    except Exception as e:
        logger.warning(f"Error cleaning up temporary files: {str(e)}")

    logger.info(f"Successfully created thumbnail: {output_file}")

def main():
    # Set up logging
    logger = setup_logging()

    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Create a thumbnail image from a Template.nrrd file and a Signal.nrrd file."
    )

    # Add arguments
    parser.add_argument(
        "template_file",
        help="Path to Template.nrrd file"
    )
    parser.add_argument(
        "signal_file",
        help="Path to Signal.nrrd file"
    )
    parser.add_argument(
        "output_file",
        help="Path to output thumbnail.png file"
    )
    parser.add_argument(
        '--cache',
        action='store_true',
        help='If added then the template mips are cached'
    )
    parser.add_argument(
        '--max_scale',
        action='store_true',
        help='If the colour scale should use the full stack rather than fit only data depth'
    )
    parser.add_argument(
        '--add_colorbar_padding',
        action='store_true',
        help='Add 2 pixels of padding to align with colorbar'
    )

    # Parse arguments
    args = parser.parse_args()

    # Create thumbnail
    create_thumbnail(
        args.template_file,
        args.signal_file,
        args.output_file,
        cache_template=args.cache,
        max_scale=args.max_scale,
        add_colorbar_padding=args.add_colorbar_padding,
        logger=logger
    )

if __name__ == "__main__":
    main()
