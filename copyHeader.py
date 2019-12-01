import numpy as np
import sys
import os
import nrrd

if (len(sys.argv) < 2):
    print('Error: missing arguments!')
    print('e.g. python copyHeader.py template.nrrd target.nrrd')
else:
    print('Loading header from %s...' % (str(sys.argv[1])))
    data1, header1 = nrrd.read(str(sys.argv[1]))
    size = np.shape(data1)
    print('Loading target image: %s...' % (str(sys.argv[2])))
    data1, header2 = nrrd.read(str(sys.argv[2]))
    if np.shape(data1) == size:
        print('Changing: ' + str(header2))
        print('Into:     ' + str(header1))
        print('Saving...')
        nrrd.write(str(sys.argv[2]), data1, header1)
        print('Updated: ' + str(sys.argv[2]))
    else:
        print('Images must be the same size!')
        print(str(size) + ' not equal to ' + str(np.shape(data1)))
