import numpy as np
import sys, os
import nrrd
from scipy import ndimage

if (len(sys.argv) < 3):
    print 'Error: missing arguments!'
    print 'e.g. python labelObjects.py image.nrrd indexlabels.nrrd [intensity_threshold] [connection_cube]'
else:
    print 'Loading image %s...'% (str(sys.argv[1]))
    data1, header1 = nrrd.read(str(sys.argv[1]))
    t=20
    sl = np.ones((3,3,3))
    if (len(sys.argv) > 3):
        t=np.uint8(sys.argv[3])
    print 'Labeling objects with any voxel intensity above %s'% str(t)

    if (len(sys.argv) > 4):
        sl=np.array(sys.argv[4],dtype=np.uint8)

    data1[data1<t]=0

    print 'identifying distinct objects...'
    labels, features = ndimage.label(data1, structure=sl)
    print str(features) + ' distinct objects found'

    print 'cleaing noise...'
    for i in range(1,features+1):
      count = np.sum(labels==i)
      if count < 3:
        labels[labels==i]=0
        features = features - 1
    print str(features) + ' distinct objects still indexed'

    print "Saving result to " + str(sys.argv[2])
    if features > 255:
      header1['type'] = 'uint16'
      nrrd.write(str(sys.argv[2]), np.uint16(labels), options=header1)
    else:
      header1['type'] = 'uint8'
      nrrd.write(str(sys.argv[2]), np.uint8(labels), options=header1)

print 'done.'
