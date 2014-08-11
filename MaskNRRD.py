import png
import numpy as np
import sys, os
import nrrd

if (len(sys.argv) < 3):
    print 'Error: missing arguments!' 
    print 'e.g. python MaskNRRD.py imageIn.nrrd mask.nrrd imageOut.nrrd' 
else:
    print 'Loading image: %s...'% (str(sys.argv[1]))
    data1, header1 = nrrd.read(str(sys.argv[1]))   
    print 'Loading mask: %s...'% (str(sys.argv[2]))
    data2, header2 = nrrd.read(str(sys.argv[2]))  
    if (data1.size <> data2.size):
        print '\n\nError: Images must be the same size!!'
    else:
        print 'Applying mask...'
        data3=data1
        data3[data2==0]=0
        print 'Saving result to %s...'% (str(sys.argv[3]))
        nrrd.write(str(sys.argv[3]), np.uint8(data3), options=header1)    
        print 'done.'    
