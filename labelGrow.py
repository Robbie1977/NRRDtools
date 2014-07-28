import numpy as np
import sys, os
import nrrd

if (len(sys.argv) < 3):
    print 'Error: missing arguments!'
    print 'e.g. python labelGrow.py template.nrrd index.nrrd [intensity_threshold] [iterations]'
else:
    print 'Loading template %s...'% (str(sys.argv[1]))
    data1, header1 = nrrd.read(str(sys.argv[1]))
    print 'Processing %s...'% (str(sys.argv[2]))
    data2, header2 = nrrd.read(str(sys.argv[2]))
    t=20
    s=2
    reps = 400
    b = np.append(np.unique(data2),[256])
    bc = np.arange(1,256)
    if (len(sys.argv) > 3):
        t=np.uint8(sys.argv[3])
    print 'Growing index for any template intensity above %s'% str(t)

    print np.histogram(data2, bins=b)
    out2 = np.array(data2)

    i = 0

    if (len(sys.argv) > 4):
        reps=np.int32(sys.argv[4])
    print 'Running for %s iteration(s)'% str(reps)

    Iout = str(sys.argv[2]).replace(".nrrd","_old.nrrd")
    nrrd.write(Iout, data2, options=header2)

    for rep in range(1,reps+1):
      data2 = np.array(out2)
      index1 = np.argwhere(np.multiply((data1>t),(data2==0)))
      print "Added: " + str(i - np.size(index1))
      print str(rep) + ' of ' + str(reps)

      if np.size(index1) != i :
        i = np.size(index1)
        for val in index1:

            g = data2[(val[0]-s):(val[0]+s),(val[1]-s):(val[1]+s),(val[2]-s):(val[2]+s)]

            if (np.sum(g) > 0):
                subhist = np.histogram(g, bins=bc)
                m=subhist[0].argmax()
                r = bc[m]
                if (subhist[0][m] > (np.sum(subhist[0])-subhist[0][m])):
                    out2[val[0],val[1],val[2]] = r
        if (np.mod(rep,50) == 0):
          print "Saving result to " + str(sys.argv[2])
          nrrd.write(str(sys.argv[2]), np.uint8(out2), options=header2)
          print np.histogram(out2, bins=b)
      else:
          print "Finishing as no change"
          break

    print "Saving result to " + str(sys.argv[2])
    nrrd.write(str(sys.argv[2]), np.uint8(out2), options=header2)
    print np.histogram(out2, bins=b)
    print 'done.'
