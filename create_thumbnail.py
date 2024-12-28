#!/usr/bin/env python3
import argparse
import os
import random
import subprocess
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

def run_subprocess(command, logger):
    """
    Run a subprocess command and handle errors.

    Parameters:
        command (list): Command and arguments to execute.
        logger (logging.Logger): Logger instance for logging messages.

    Returns:
        bool: True if command succeeds, False otherwise.
    """
    logger.debug(f"Executing command: {' '.join(command)}")
    try:
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.debug(f"Command output: {result.stdout}")
        if result.stderr:
            logger.warning(f"Command stderr: {result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {' '.join(command)}")
        logger.error(f"Return code: {e.returncode}")
        logger.error(f"Output: {e.output}")
        logger.error(f"Error Output: {e.stderr}")
        return False

def create_thumbnail(template_file, signal_file, output_file, cache_template=False, max_scale=False, logger=None):
    """
    Create a thumbnail by processing template and signal NRRD files.

    Parameters:
        template_file (str): Path to the Template.nrrd file.
        signal_file (str): Path to the Signal.nrrd file.
        output_file (str): Path to the output thumbnail.png file.
        cache_template (bool): Whether to cache template MIPs.
        max_scale (bool): Whether to use max scale for colorization.
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
        mip_command = [
            sys.executable, create_mip_path, template_file, template_mip
        ]
        if not run_subprocess(mip_command, logger):
            logger.error("Failed to create template MIP.")
            sys.exit(1)
    else:
        logger.info(f"Using cached template MIP: {template_mip}")

    # Colorize the signal image
    signal_colorized = f"signal_colorized_{rand_num}.png"
    if max_scale:
        logger.info("Producing with max scale...")
        colorize_command = [
            sys.executable, colorize_image_stack_path,
            "--nrrd", signal_file,
            "--png", signal_colorized,
            "--scale",
            "--max"
        ]
    else:
        colorize_command = [
            sys.executable, colorize_image_stack_path,
            "--nrrd", signal_file,
            "--png", signal_colorized,
            "--scale"
        ]
    if not run_subprocess(colorize_command, logger):
        logger.error("Failed to colorize signal image.")
        # Clean up and exit
        if not cache_template and os.path.exists(template_mip):
            os.remove(template_mip)
            logger.debug(f"Removed temporary file: {template_mip}")
        sys.exit(1)

    # Verify the signal file exists before merging
    if not os.path.exists(signal_colorized):
        logger.error(f"Signal file not found before merge: {signal_colorized}")
        sys.exit(1)
    else:
        logger.info(f"Signal file exists before merge: {signal_colorized}")
    
    # Merge the template and colorized signal images
    merge_command = [
        sys.executable, merge_images_path,
        template_mip,
        signal_colorized,
        output_file
    ]
    if not run_subprocess(merge_command, logger):
        logger.error("Failed to merge images.")
        # Clean up and exit
        if not cache_template and os.path.exists(template_mip):
            os.remove(template_mip)
            logger.debug(f"Removed temporary file: {template_mip}")
        if os.path.exists(signal_colorized):
            os.remove(signal_colorized)
            logger.debug(f"Removed temporary file: {signal_colorized}")
        sys.exit(1)

    logger.info(f"Successfully created thumbnail: {output_file}")

    # Clean up temporary files
    try:
        if not cache_template and os.path.exists(template_mip):
            os.remove(template_mip)
            logger.debug(f"Removed temporary file: {template_mip}")
    except Exception as e:
        logger.warning(f"Could not remove template MIP file: {template_mip}. Error: {e}")

    try:
        if not cache_template and os.path.exists(signal_colorized):
            os.remove(signal_colorized)
            logger.debug(f"Removed temporary file: {signal_colorized}")
    except Exception as e:
        logger.warning(f"Could not remove signal colorized file: {signal_colorized}. Error: {e}")

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

    # Parse arguments
    args = parser.parse_args()

    # Create thumbnail
    create_thumbnail(
        args.template_file,
        args.signal_file,
        args.output_file,
        cache_template=args.cache,
        max_scale=args.max_scale,
        logger=logger
    )

if __name__ == "__main__":
    main()
