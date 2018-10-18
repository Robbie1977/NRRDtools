import numpy as np
import sys, os
import nrrd
from scipy import ndimage

if (len(sys.argv) < 2):
    print('Error: missing arguments!')
    print('e.g. python centreOfMass.py imageIn.nrrd')
else:
    Iin = str(sys.argv[1])
    data1, header1 = nrrd.read(Iin)

    print(list(np.array(ndimage.measurements.center_of_mass(Iin),dtype=np.int)))
    
