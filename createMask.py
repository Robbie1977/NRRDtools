import numpy as np
import sys
import os
import nrrd

# Default threshold, number of positive voxels in the neighborhood, and the size of the neighborhood
th = 35
pt = 3
bs = 5

def create_mask(input_file, output_file=None):
    """
    Create a binary mask from an input NRRD file using a threshold value.

    :param input_file: str, path to the input NRRD file
    :param output_file: str (optional), path to the output NRRD file. If not specified, the output file will have the same name as the input file but with the '-MD.nrrd' extension
    """
    if output_file is None:
        output_file = input_file.replace(".nrrd", "-MD.nrrd")

    # Load input data
    data, header = nrrd.read(input_file)

    # Create binary mask
    mask = np.zeros_like(data, dtype=np.uint8)
    mask[data > th] = np.uint8(255)

    # Remove isolated voxels
    # for x in range(bs, mask.shape[0] - bs):
    #     for y in range(bs, mask.shape[1] - bs):
    #         for z in range(bs, mask.shape[2] - bs):
    #             if np.sum(mask[x-bs:x+bs, y-bs:y+bs, z-bs:z+bs]) < pt*255 and mask[x, y, z] > 0:
    #                 mask[x, y, z] = 0
    #                 sys.stdout.write('.')

    # Save binary mask as NRRD file
    nrrd.write(output_file, mask, options=header)

    print(f"Saved binary mask to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: missing arguments!")
        print("e.g. python createMask.py input.nrrd [output.nrrd]")
    else:
        input_file = str(sys.argv[1])
        output_file = None
        if len(sys.argv) > 2:
            output_file = str(sys.argv[2])

        create_mask(input_file, output_file=output_file)
