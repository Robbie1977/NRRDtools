import png
import numpy as np
import sys, os
import nrrd

if (len(sys.argv) < 3):
    print('Error: missing arguments!') 
    print('e.g. python labelShrink.py template.nrrd index.nrrd minimumIntensity') 
else:
    print('Loading template: %s...'% (str(sys.argv[1])))
    data1, header1 = nrrd.read(str(sys.argv[1]))   
    print('Loading index: %s...'% (str(sys.argv[2])))
    data2, header2 = nrrd.read(str(sys.argv[2]))  
    th = np.uint8(sys.argv[3])
    if (data1.size != data2.size):
        print('\n\nError: Images must be the same size!!')
    else:
        print('Removing any index for intensity values below %s...'% str(th))
        data3=data2
        data3[data1<th]=np.uint8(0)
        print('Saving result to %s...'% (str(sys.argv[2])))
        nrrd.write(str(sys.argv[2]), np.uint8(data3), options=header2)    
        print('done.')
        
