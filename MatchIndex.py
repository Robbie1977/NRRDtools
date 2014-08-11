import numpy as np
import sys, os
import nrrd

if (len(sys.argv) < 4):
    print 'Error: missing arguments!' 
    print 'e.g. python matchIndex.py indexfile.nrrd intensity(0-254) imagefile.nrrd [outputfile.csv]' 
else:
    data1, header1 = nrrd.read(str(sys.argv[1]))
    data2, header2 = nrrd.read(str(sys.argv[3]))
    result = "["
    div = ""
    if (data1.size <> data2.size):
        print '\n\nError: Images must be the same size!!'
    else:
        for val in np.unique(data1):
            if (val > 0):
#                print val
#                print np.sum(data2[data1==np.uint8(val)])
#                print np.max(data2[data1==np.uint8(val)])
                if (np.max(data2[data1==np.uint8(val)]) > np.uint8(sys.argv[2])):
                    result = result + div + str(val).zfill(2)
                    div = ", "
        result = result + "]"
        
        print result
        
        if (len(sys.argv) > 4):
            with open(str(sys.argv[4]), "a") as myfile: 
                myfile.write(str(sys.argv[1]) + ', ' + str(sys.argv[2]) + ', ' + str(sys.argv[3]) + ', ' + result + '\n')
                    
