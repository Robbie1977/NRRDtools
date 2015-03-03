import numpy as np
import sys, os
import nrrd

if (len(sys.argv) < 2):
    print '0'
else:
    Iin = str(sys.argv[1])

    data1, header1 = nrrd.read(Iin)
    sh = np.shape(data1)

    print '%s'% (sh[2])
