import numpy as np
import sys, os
import nrrd

if (len(sys.argv) < 2):
    print 'Error: missing arguments!'
    print 'e.g. python brightestSlice.py image.nrrd'
else:
    Iin = str(sys.argv[1])
    print 'Processing %s...'% (Iin)
    data1, header1 = nrrd.read(Iin)

    sh = np.shape(data1)
    print 'Image Size X:%s,Y:%s,Z:%s'% sh

    data1 = data1.sum(axis=0)
    data1 = data1.sum(axis=0)

    sh = np.shape(data1)

    mp = np.argmax(data1)

    print 'Number of slice %s'% (sh)
    
    print 'Max combined intensity occurs at slice %s'% (mp)
