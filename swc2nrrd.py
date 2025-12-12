#!/usr/bin/env python3
import argparse
import numpy as np
import nrrd
import navis
from nrrd_to_swc import convert_swc_to_nrrd

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert SWC file to NRRD file using navis")
    parser.add_argument("swc_file", help="Path to input SWC file")
    parser.add_argument("template_file", help="Path to input template NRRD file")
    parser.add_argument("output_file", help="Path to output NRRD file")
    args = parser.parse_args()
    
    convert_swc_to_nrrd(args.swc_file, args.template_file, args.output_file)
