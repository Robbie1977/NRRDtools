import numpy as np
import sys, os
import nrrd

if (len(sys.argv) < 2):
    print '0'
else:
    Iin = str(sys.argv[1])

    data1, header1 = nrrd.read(Iin)

    data1 = data1.sum(axis=0)
    data1 = data1.sum(axis=0)

    mp = np.argmax(data1)

    print '%s'% (mp)
