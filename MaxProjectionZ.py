import png
import numpy as np
import sys, os
import nrrd

if (len(sys.argv) < 2):
    print 'Error: missing arguments!' 
    print 'e.g. python MaxProjectionZ.py image.nrrd' 
else:
    print 'Loading %s...'% (str(sys.argv[1]))
    data1, header1 = nrrd.read(str(sys.argv[1]))   
    print 'Processing %s...'% (str(sys.argv[1]))
    proj = np.max(data1)
    pName = str(sys.argv[1]).replace('.nrrd','.png')
    png.from_array(proj, 'L').save(pName)  
    print 'done.'    



