import nrrd
import sys
import numpy as np

def check_swc(volume_swc, volume_nrrd):
    """
    This function checks the SWC file against the corresponding NRRD volume file.
    It prints any line in the SWC file where the corresponding voxel in the NRRD volume has a value of 0.

    Args:
        volume_swc (str): Path to the SWC file.
        volume_nrrd (str): Path to the NRRD volume file.
    """

    data, header = nrrd.read(volume_nrrd)

    with open(volume_swc) as f:
        lines = [line.strip() for line in f]

    name = True
    count = 0

    for line in lines:
        if '#' not in line:
            values = line.split(' ')
            xl = int(np.floor(np.float(values[2]) / header['space directions'][0][0]))
            yl = int(np.floor(np.float(values[3]) / header['space directions'][1][1]))
            zl = int(np.floor(np.float(values[4]) / header['space directions'][2][2]))
            xh = int(np.ceil(np.float(values[2]) / header['space directions'][0][0]) + 1)
            yh = int(np.ceil(np.float(values[3]) / header['space directions'][1][1]) + 1)
            zh = int(np.ceil(np.float(values[4]) / header['space directions'][2][2]) + 1)
            value = data[xl:xh, yl:yh, zl:zh]
            if np.sum(value) < 1:
                if name:
                    print(volume_swc)
                    name = False
                print(line)
                count += 1
    if count > 0:
        print(count)


if len(sys.argv) < 3:
    print('Error: missing arguments!')
    print('e.g. python checkSWC.py volume.swc volume.nrrd')
else:
    check_swc(sys.argv[1], sys.argv[2])
