import numpy as np
import sys, os
import nrrd

if (len(sys.argv) < 2):
    print('Error: missing arguments!')
    print('e.g. python countVoxels.py imageIn.nrrd [level (0-255)]')
else:
    Iin = str(sys.argv[1])
    level = 10
    if len(sys.argv) > 2:
        level = np.uint8(sys.argv[2])
    result = 0
    data, header = nrrd.read(Iin)
    voxels = data > level
    result = np.sum(voxels)
    print(result)