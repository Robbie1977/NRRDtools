# Script for converting nanometer units to microns also adding swc soma label.  

import sys
import numpy as np


if (len(sys.argv) < 1):
    print('Error: missing arguments!')
    print('e.g. python modSWC.py')
else:

    lines = [line.strip() for line in open(str(sys.argv[1]))]

    out = []

    name = True

    for line in lines:
        if '#' not in line:
            values = line.split(' ')
            values[2] = str(np.divide(np.double(values[2]),1000.0))
            values[3] = str(np.divide(np.double(values[3]),1000.0))
            values[4] = str(np.divide(np.double(values[4]),1000.0))
            
            if np.double(values[5]) > 0:
                values[5] = str(np.divide(np.double(values[5]),1000.0))
                if np.int(values[0]) == 1 and np.int(values[1]) == 0:
                  values[1] = str(np.int(1))
            out.append(' '.join(values))
        else:
            if 'Created by' not in line:
              out.append(line)
            else:
              out.append(line + '; Scaled to microns (1/1000) by https://github.com/Robbie1977/NRRDtools/blob/master/modCatmaidSWC.py')
    File_object = open(str(sys.argv[1]),"w")
    File_object.writelines('\n'.join(out)) 
    File_object.close() 
    print('Converted ' + str(sys.argv[1]))
