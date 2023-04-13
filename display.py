import numpy as np
import sys, os
import nrrd
from mayavi.mlab import *

if (len(sys.argv) < 2):
    print('Error: missing arguments!') 
    print('e.g. python matchIndex.py indexfile.nrrd intensity(0-254) imagefile.nrrd [outputfile.csv]') 
else:
    data1, header1 = nrrd.read(str(sys.argv[1]))
    s = data1/255.0
    pipeline.volume(pipeline.scalar_field(s))
    #contour3d(data1, transparent=True)
    #show()