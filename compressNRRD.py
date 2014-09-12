import numpy as np
import sys, os
import nrrd

if (len(sys.argv) < 2):
    print 'Error: missing arguments!'
    print 'e.g. python compressNRRD.py imageIn.nrrd [ImageOut.nrrd]'
else:
    print 'Processing %s...'% (str(sys.argv[1]))
    data1, header1 = nrrd.read(str(sys.argv[1]))
    print header1
    header1['encoding'] = 'gzip'
    if header1['space directions'] == ['none', 'none', 'none']:
        header1.pop("space directions", None)
    print header1
    print 'saving...'
    if (len(sys.argv) == 3):
      nrrd.write(str(sys.argv[2]), data1, options=header1)
      print 'saved to ' + str(sys.argv[2])
    else:
      nrrd.write(str(sys.argv[1]), data1, options=header1)
      print 'saved to ' + str(sys.argv[1])
