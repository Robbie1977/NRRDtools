import numpy as np
import sys, os
import nrrd

if (len(sys.argv) < 3):
    print 'Error: missing arguments!'
    print 'e.g. python compressNRRD.py imageIn.nrrd left-posterior-superior [ImageOut.nrrd]'
    print 'orientation is ordered X,Y,Z; highest value: [left/right],[anterior/posterior],[superior/inferior].'
else:
    print 'Processing %s...'% (str(sys.argv[1]))
    data1, header1 = nrrd.read(str(sys.argv[1]))
    print header1
    header1['space'] = str(sys.argv[2])
    header1.pop("space dimension", None)
    print header1
    print 'saving...'
    if (len(sys.argv) == 4):
      nrrd.write(str(sys.argv[3]), data1, options=header1)
      print 'saved to ' + str(sys.argv[3])
    else:
      nrrd.write(str(sys.argv[1]), data1, options=header1)
      print 'saved to ' + str(sys.argv[1])
