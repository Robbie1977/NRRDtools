import numpy as np
import sys, os
import nrrd

if (len(sys.argv) < 4):
    print 'Error: missing arguments!'
    print 'e.g. python addPadding.py #AddedSlicesLowEnd #AddedSlicesHighEnd imageIn.nrrd [imageOut.nrrd]'
else:
    Iin = str(sys.argv[3])
    print 'Processing %s...'% (Iin)
    data1, header1 = nrrd.read(Iin)

    sh = np.shape(data1)

    Lpad = int(sys.argv[1])
    Hpad = int(sys.argv[2])

    data = np.zeros([sh[0],sh[1],sh[2]+Lpad+Hpad], dtype=np.uint8)
    data[0:sh[0],0:sh[1],Lpad:Lpad+sh[2]] = data1

    if (len(sys.argv) > 4):
      Iout = str(sys.argv[4])
      nrrd.write(Iout, data, options=header1)
      print 'saved to ' + Iout
    else:
      Iout = Iin.replace(".nrrd", "_" + str(sh[2]) + ".nrrd")
      nrrd.write(Iout, data1, options=header1)
      print 'original saved to ' + Iout
      nrrd.write(Iin, data, options=header1)
      print 'padded version saved to ' + Iout
