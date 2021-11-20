import numpy as np
import sys, os
import nrrd

if (len(sys.argv) < 2):
    print('Error: missing arguments!')
    print('e.g. python mergeNRRDs.py imageOut.nrrd imageIn1.nrrd [ImageIn#.nrrd...]')
else:
    Iout = str(sys.argv[1])
    brightest = 0
    level = 255;
    bright = ""
    errorOn = ""
    dataMax = 0
    dataBk = 0
    result = []
    for i in range(2,len(sys.argv)):
        dataBk = np.copy(result)
        Iin = str(sys.argv[i])
        print('Processing %s...'% (Iin))
        data, header = nrrd.read(Iin)
        sh = np.shape(data)
        if (dataMax < np.max(data)):
            dataMax = np.max(data)
        if (dataMax > 255):
            scale = dataMax/255
            print("Scalling (" + str(scale) + ")...")
            data = np.uint8(data/scale)
            data[data > 255] = np.uint8(255)
        if (i == 2):
            result = np.uint8(data)
            shTest = sh
            brightest = np.sum(data)
        else:
            if (sh == shTest):
                result = np.maximum(result, data, dtype=np.uint8)
            else:
                print('ERROR: %s not the same size!' + str(sh) + ' - ' + str(shTest))

    normData = np.uint8(result)

    nrrd.write(Iout, normData, header=header)
    print('saved to ' + Iout)
