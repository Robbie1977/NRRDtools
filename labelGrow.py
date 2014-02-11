import numpy as np
import sys, os
import nrrd

if (len(sys.argv) < 3):
    print 'Error: missing arguments!' 
    print 'e.g. python labelGrow.py template.nrrd index.nrrd [intensity_threshold]' 
else:
    print 'Loading template %s...'% (str(sys.argv[1]))
    data1, header1 = nrrd.read(str(sys.argv[1]))
    print 'Processing %s...'% (str(sys.argv[2]))
    data2, header2 = nrrd.read(str(sys.argv[2]))
    t=200
    s=2
    b = np.append(np.unique(data2),[256]) 
    bc = np.arange(1,255)
    if (len(sys.argv) > 3):
        t=np.uint8(sys.argv[3])
    print 'Growing index for any template intensity above %s'% str(t)
    
    index1 = np.argwhere(np.multiply((data1>t),(data2==0)))
    out2 = np.array(data2)
    print np.size(index1)
    print np.histogram(data2, bins=b)
    i=0
    
    for val in index1:
#        i = i + 1
        g = data2[(val[0]-s):(val[0]+s),(val[1]-s):(val[1]+s),(val[2]-s):(val[2]+s)]

        if (np.sum(g) > 0):
            subhist = np.histogram(g, bins=bc)
            m=subhist[0].argmax()
            r = bc[m]
            if (subhist[0][m] > (np.sum(subhist[0])-subhist[0][m])):
                out2[val[0],val[1],val[2]] = r
#            else:
#                print subhist[0][0:6]
#                print val
#                print g
#                print '%s - %s'% (str(r), str(w-i))          
        
#        for sval in subindex1: 
#            print data1[(val[0]-r)+sval[0],(val[1]-r)+sval[1],(val[2]-r)+sval[2]]
        
#            lst = index1[index1[:,0]==val[0]]
#            lst = lst[lst[:,2]==val[2]]
#            ep = np.max(lst[:,1])
#            if (ep > val[1]):
#                out1[val[0],val[1]:ep,val[2]]=tv
#                skp[val[0],val[2]]=ep
##                print val
#    print np.histogram(out1, bins=np.unique(out1))
#    for v in np.unique(data1[data1>0]):
#        out1[data1==v]=v            
    nrrd.write('/Volumes/Macintosh HD/Users/robertcourt/BTSync/testout.nrrd', np.uint8(out2), options=header2)    
    print np.histogram(out2, bins=b)
    print 'done.'    
    