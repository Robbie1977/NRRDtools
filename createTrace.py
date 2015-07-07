import numpy as np
import sys, os
import nrrd
from scipy import ndimage

th = 35
pt = 3
bs = 5

if (len(sys.argv) < 2):
    print 'Error: missing arguments!'
    print 'e.g. python createTrace.py imageIn.nrrd [ImageOut.nrrd]'
else:
    Iin = str(sys.argv[1])
    print 'Processing %s...'% (Iin)
    data1, header1 = nrrd.read(Iin)

    sh = np.shape(data1)

    if (len(sys.argv) > 2):
      Iout = str(sys.argv[2])
    else:
      Iout = Iin.replace(".nrrd", "-TD.nrrd")

    data = np.zeros(sh, dtype=np.uint8)
    for z in range(0,sh[2]-1):
        print 'processing slice ' + str(z) + ' of ' + str(sh[2]-1)
        for y in range(0,sh[1]-1):
            x = 0
            if np.sum(data1[x:sh[0]-1,y,z])<th:
                continue
            while x < int((sh[0]/2)-1):
                if data1[x,y,z]>th:
                    data[x,y,z] = np.uint8(255)
                    break
                if x+100<sh[0]-1:
                    if np.sum(data1[x:x+100,y,z])<th:
                        x+=100
                        continue
                if x+10<sh[0]-1:
                    if np.sum(data1[x:x+10,y,z])<th:
                        x+=10
                        continue
                x+=1
            x=sh[0]-1
            while x > 0:
                if data1[x,y,z]>th:
                    data[x,y,z] = np.uint8(255)
                    break
                if x>100:
                    if np.sum(data1[x-100:x,y,z])<th:
                        x-=100
                        continue
                if x>10:
                    if np.sum(data1[x-10:x,y,z])<th:
                        x-=10
                        continue
                x-=1
    # print 'cleaning noise...'
    # data = ndimage.median_filter(data, 3)

    nrrd.write(Iout, data, options=header1)
    print 'saved to ' + Iout
