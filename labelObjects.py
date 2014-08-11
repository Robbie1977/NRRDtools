import numpy as np
import sys, os
import nrrd
from scipy import ndimage

if (len(sys.argv) < 3):
    print 'Error: missing arguments!'
    print 'e.g. python labelObjects.py image.nrrd indexlabels.nrrd [intensity_threshold] [min_size] [connection_cube]'
else:
    print 'Loading image %s...'% (str(sys.argv[1]))
    data1, header1 = nrrd.read(str(sys.argv[1]))
    header1.pop("endian", None)
    t=20
    ms=1000
    sl = np.ones((3,3,3))
    if (len(sys.argv) > 3):
        t=np.uint16(sys.argv[3])
    print 'Labeling objects with any voxel intensity above %s'% str(t)

    if (len(sys.argv) > 4):
        ms=np.array(sys.argv[4],dtype=np.uint16)

    if (len(sys.argv) > 5):
        sl=np.array(sys.argv[5],dtype=np.uint16)

    data1[data1<t]=0

    print 'identifying distinct objects...'
    labels, features = ndimage.label(data1, structure=sl)
    print str(features) + ' distinct objects found'
    val, lab = np.histogram(labels, bins=range(1,features+1))
    print 'Removing any objects with a volume of less than ' + str(ms) + ' voxels.'
    print 'New label(s):'
    data = np.zeros(np.shape(data1))
    v=1
    for i in range(0,features-1):
      if val[i] > ms:
        data[labels==lab[i]]=v
        print str(v) + ' = ' + str(lab[i])
        v=v+1
    print str(v-1) + ' distinct objects still indexed'

    print "Saving result to " + str(sys.argv[2])
    header1['encoding'] = 'gzip'
    if v > 256:
      header1['type'] = 'uint16'
      nrrd.write(str(sys.argv[2]), np.uint16(data), options=header1)
    else:
      header1['type'] = 'uint8'
      nrrd.write(str(sys.argv[2]), np.uint8(data), options=header1)

print 'done.'
