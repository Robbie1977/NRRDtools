import numpy as np
import sys, os
import nrrd

if (len(sys.argv) < 2):
    print 'Error: missing arguments!'
    print 'e.g. python createMask.py imageOut.nrrd imageIn1.nrrd [ImageIn#.nrrd...]'
else:
    Iout = str(sys.argv[1])
    for i in range(2,len(sys.argv)):
        Iin = str(sys.argv[i])
        print 'Processing %s...'% (Iin)
        data, header = nrrd.read(Iin)
        sh = np.shape(data)
        if (i == 2):
            dataSum = np.int64(data);
            shTest = sh;
        else:
            if (sh == shTest):
                dataSum = dataSum + np.int64(data);
            else:
                print 'ERROR: %s not the same size!'% (Iin)

    dataMin = np.min(dataSum)
    dataMax = np.max(dataSum)

    normData = np.uint8(np.round(np.mulitply(np.divide(np.subtract(dataSum, dataMin),np.float(dataMax)),255.0)))

    nrrd.write(Iout, data, options=header)
    print 'saved to ' + Iout
