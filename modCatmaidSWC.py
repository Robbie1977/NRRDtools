# Script for converting units to microns (/1000) also add swc soma label.  

import sys
import numpy as np


if (len(sys.argv) < 1):
    print 'Error: missing arguments!'
    print 'e.g. python modSWC.py'
else:

    lines = [line.strip() for line in open(str(sys.argv[1]))]

    out = []

    name = True
    count = 0

    for line in lines:
        if '#' not in line:
            values = line.split(' ')
            values[2] = np.divide(np.double(values[2]),1000.0)
            values[3] = np.divide(np.double(values[3]),1000.0)
            values[4] = np.divide(np.double(values[4]),1000.0)
            
            if np.double(values[5]) > 0:
                values[5] = np.divide(np.double(values[5]),1000.0)
                if np.int(values[0]) == 1 && np.int(values[1]) == 0:
                  values[1] = np.int(1)
            out[count] = values.join(' ')
        else:
            if 'Created by' not in line:
              out[count] = line
            else:
              out[count] = line + '; Scaled to microns (1/1000) by https://github.com/Robbie1977/NRRDtools/blob/master/modCatmaidSWC.py'
        count += 1
    File_object = open(str(sys.argv[1]),"w")
    File_object.writelines(L) for L = out
    File_object.close() 
