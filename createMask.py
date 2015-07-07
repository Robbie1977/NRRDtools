import numpy as np
import sys, os
import nrrd

th = 35
pt = 3
bs = 5

if (len(sys.argv) < 2):
    print 'Error: missing arguments!'
    print 'e.g. python createMask.py imageIn.nrrd [ImageOut.nrrd]'
else:
    Iin = str(sys.argv[1])
    print 'Processing %s...'% (Iin)
    data1, header1 = nrrd.read(Iin)

    sh = np.shape(data1)

    if (len(sys.argv) > 2):
      Iout = str(sys.argv[2])
    else:
      Iout = Iin.replace(".nrrd", "-MD.nrrd")


    data = np.zeros(sh, dtype=np.uint8)
    data[data1>th] = np.uint8(255)

    # for x in range(5,sh[0]-6):
    #   for y in range(5,sh[1]-6):
    #     for z in range(5,sh[2]-6):
    #       if ((np.sum(data[x-bs:x+bs,y-bs:y+bs,z-bs:z+bs]) < (pt*255)) and (data[x,y,z] > 0)):
    #         data[x,y,z] = 0
    #         sys.stdout.write('.')

    nrrd.write(Iout, data, options=header1)
    print 'saved to ' + Iout
