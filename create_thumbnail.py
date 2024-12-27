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
    # Use current working directory for script paths like the old version
    scripts_dir = os.getcwd()
    merge_images_path = os.path.join(scripts_dir, "merge_images.py")
    colorize_image_stack_path = os.path.join(scripts_dir, "colorize_image_stack.py")
    create_mip_path = os.path.join(scripts_dir, "create_mip.py")

    rand_num = str(random.randint(1000, 9999))
    
    # Use the same template MIP naming as the old version
    if cache_template:
        template_id = os.path.basename(os.path.dirname(template_file))
        template_mip = f"template_mip_{template_id}.png"
    else:
        template_mip = f"template_mip_{rand_num}.png"

    # Use direct system calls like the old version
    if not cache_template or not os.path.exists(template_mip):
        os.system(f"python3 {create_mip_path} {template_file} {template_mip}")
    
    signal_colorized = f"signal_colorized_{rand_num}.png"
    if max_scale:
        logger.info('Producing with max scale...')
        os.system(f"python3 {colorize_image_stack_path} --nrrd {signal_file} --png {signal_colorized} --scale --max")
    else:
        os.system(f"python3 {colorize_image_stack_path} --nrrd {signal_file} --png {signal_colorized} --scale")
    
    os.system(f"python3 {merge_images_path} {template_mip} {signal_colorized} {output_file}")

    # Clean up
    if not cache_template and os.path.exists(template_mip):
        os.remove(template_mip)
    if os.path.exists(signal_colorized):
        os.remove(signal_colorized)

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
