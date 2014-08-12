import numpy as np
import sys, os
import nrrd
from scipy import ndimage

def labelObj(imagefile, labelfile, t=20, ms=1000, sl=np.ones((3,3,3))):
    print 'Loading image %s...'% (imagefile)
    data1, header1 = nrrd.read(imagefile)
    header1.pop("endian", None)

    print 'Labeling objects with any voxel intensity above %s'% str(t)

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

    print "Saving result to " + labelfile
    header1['encoding'] = 'gzip'
    if v > 256:
      header1['type'] = 'uint16'
      nrrd.write(labelfile, np.uint16(data), options=header1)
    else:
      header1['type'] = 'uint8'
      nrrd.write(labelfile, np.uint8(data), options=header1)
    return np.uint8(np.unique(data))

def cutObj(imagefile, labelfile, labels=None):
    if labels is None:
      print 'no labels to be cut'
    else:
      print 'Loading image %s...'% (imagefile)
      data1, header1 = nrrd.read(imagefile)
      print 'Loading mask %s...'% (labelfile)
      data2, header2 = nrrd.read(imagefile)

      print 'Cutting objects with label(s) %s'% str(labels)

      for i in labels:
        print 'Cutting object ' + str(i)
        data1[data2==i] = 0

      v=np.max(data1)
      print "Saving result over " + imagefile
      header1['encoding'] = 'gzip'
      if v > 256:
        header1['type'] = 'uint16'
        nrrd.write(imagefile, np.uint16(data1), options=header1)
      else:
        header1['type'] = 'uint8'
        nrrd.write(imagefile, np.uint8(data1), options=header1)

def cropObj(imagefile, labelfile, labels=None):
    if labels is None:
      print 'no labels to crop to'
    else:
      print 'Loading image %s...'% (imagefile)
      data1, header1 = nrrd.read(imagefile)
      print 'Loading mask %s...'% (labelfile)
      data2, header2 = nrrd.read(imagefile)

      print 'Croping to objects with label(s) %s'% str(labels)

      mask = np.ones(np.shape(data1))
      for i in labels:
        mask[np.uint8(data2)==np.uint8(i)] = 0

      data1[mask] = 0

      v=np.max(data1)
      print "Saving result over " + imagefile
      header1['encoding'] = 'gzip'
      if v > 256:
        header1['type'] = 'uint16'
        nrrd.write(imagefile, np.uint16(data1), options=header1)
      else:
        header1['type'] = 'uint8'
        nrrd.write(imagefile, np.uint8(data1), options=header1)

if __name__ == "__main__":
  if (len(sys.argv) < 3):
      print 'Error: missing arguments!'
      print 'e.g. python labelObjects.py image.nrrd indexlabels.nrrd [intensity_threshold] [min_size] [connection_cube]'
  else:
      imagefile = str(sys.argv[1])
      labelfile = str(sys.argv[2])

      if (len(sys.argv) > 3):
          t=np.uint16(sys.argv[3])

      if (len(sys.argv) > 4):
          ms=np.array(sys.argv[4],dtype=np.uint16)

      if (len(sys.argv) > 5):
          sl=np.array(sys.argv[5],dtype=np.uint16)

      labelObj(imagefile, labelfile)

  print 'done.'
