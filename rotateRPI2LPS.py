import numpy as np
import sys, os
import nrrd

if (len(sys.argv) < 2):
    print 'Error: missing arguments!'
    print 'e.g. python rotateRPI2LPS.py imageIn.nrrd [ImageOut.nrrd]'
    print 'rotate RPI to LPS orientation for CMTK (as it doesn't like RPI)'
else:
    print 'Processing %s...'% (str(sys.argv[1]))
    data1, header1 = nrrd.read(str(sys.argv[1]))
    print header1
    header1['space'] = 'left-posterior-superior'
    header1.pop("space dimension", None)
    print header1
    data2 = np.flip(data1, (0, 2))
    print 'saving...'
    if (len(sys.argv) == 3):
      nrrd.write(str(sys.argv[2]), data2, header1)
      print 'saved to ' + str(sys.argv[3])
    else:
      nrrd.write(str(sys.argv[1]), data2, header1)
      print 'saved to ' + str(sys.argv[1])
