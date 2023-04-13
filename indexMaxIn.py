import numpy as np
import sys
import os
import nrrd

if len(sys.argv) < 2:
    print('Error: missing arguments!')
    print('e.g. python indexMaxIn.py signal.nrrd [indexvalue]')
else:
    print('Loading {}...'.format(str(sys.argv[1])))
    data1, header1 = nrrd.read(str(sys.argv[1]))
    id = 255
    if len(sys.argv) > 2:
        id = np.uint8(sys.argv[2])
    data2 = np.zeros(np.shape(data1), dtype=np.uint8)
    val = np.unravel_index(data1.argmax(), data1.shape)
    data2[val[0], val[1], val[2]] = id
    Iout = str(sys.argv[1]).replace(".nrrd", "-index.nrrd")
    print("Saving result to " + Iout)
    nrrd.write(Iout, np.uint8(data2), options=header1)
