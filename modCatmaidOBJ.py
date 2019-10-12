# Script for converting nanometer units to microns.  

import sys
import numpy as np


if (len(sys.argv) < 1):
    print 'Error: missing arguments!'
    print 'e.g. python modSWC.py'
else:

    lines = [line.strip() for line in open(str(sys.argv[1]))]

    out = ['####','#','# Scaled from nanometer units to microns by https://github.com/Robbie1977/NRRDtools/blob/master/modCatmaidOBJ.py','#','####']

    for line in lines:
        if '#' not in line and 'v' in line:
            values = line.split(' ')
            values[1] = str(np.divide(np.double(values[1]),1000.0))
            values[2] = str(np.divide(np.double(values[2]),1000.0))
            values[3] = str(np.divide(np.double(values[3]),1000.0))
            
            out.append(' '.join(values))
        else:
            out.append(line)
    File_object = open(str(sys.argv[1]),"w")
    File_object.writelines('\n'.join(out)) 
    File_object.close() 
    print('Converted ' + str(sys.argv[1]))
