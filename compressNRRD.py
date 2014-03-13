import numpy as np
import sys, os
import nrrd

if (len(sys.argv) < 2):
    print 'Error: missing arguments!' 
    print 'e.g. python compressNRRD.py image.nrrd' 
else:
    print 'Processing %s...'% (str(sys.argv[1]))
    data1, header1 = nrrd.read(str(sys.argv[1]))   
    nrrd.write(str(sys.argv[1]), data1, options=header1)    
    print 'done.'    
    