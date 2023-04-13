import numpy as np
import sys, os
import nrrd

if (len(sys.argv) < 2):
    print('Error: missing arguments!')
    print('e.g. python mergeData_MP.py imageOut.nrrd imageIn1.nrrd [ImageIn#.nrrd...]')
else:
    Iout = str(sys.argv[1])
    brightest = 0
    level = 255;
    bright = ""
    errorOn = ""
    dataSum = 0
    dataBk = 0
    for i in range(2,len(sys.argv)):
        try:
            dataBk = np.copy(dataSum)
            Iin = str(sys.argv[i])
            print('Processing %s...'% (Iin))
            data, header = nrrd.read(Iin)
            sh = np.shape(data)
            if (i == 2):
                dataSum = np.uint64(data)
                shTest = sh
                brightest = np.sum(data)
            else:
                if (sh == shTest):
                    if (np.max(data) > level):
                        level = np.max(data)
                    print(str(np.max(data)))
                    dataSum = dataSum + np.uint64(data)
                else:
                    print('ERROR: %s not the same size!' + str(sh) + ' - ' + str(shTest))
        except:
            print("Unexpected error:", sys.exc_info()[0])
            dataSum = np.uint64(dataBk)
            errorOn += ', ' + Iin
        dataSum[dataSum > 255] = np.uint64(255)

    dataMin = np.min(dataSum)
    dataMax = np.max(dataSum)

    normData = np.uint8(dataSum)

    nrrd.write(Iout, normData, options=header)
    print('saved to ' + Iout)
