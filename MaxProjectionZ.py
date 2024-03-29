# example to run over multiple files: find . -name "*SG*.nrrd" -exec python ~/GIT/NRRDtools/MaxProjectionZ.py '{}' \;
import png
import numpy as np
import sys, os
import nrrd

if (len(sys.argv) < 2):
    print('Error: missing arguments!') 
    print('e.g. python MaxProjectionZ.py image.nrrd') 
else:
    print('Loading %s...'% (str(sys.argv[1])))
    data1, header1 = nrrd.read(str(sys.argv[1]))   
    print('Processing %s...'% (str(sys.argv[1])))
    proj = data1.max(2)
    pName = str(sys.argv[1]).replace('.nrrd','.png')
    print(np.shape(data1))
    print(np.shape(proj))
    print('Saving %s...'% (pName))
    png.from_array(proj, 'L').save(pName)
    print('done.')    



