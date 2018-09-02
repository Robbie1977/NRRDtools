import numpy as np
import sys, os
import nrrd

scale=1

if (len(sys.argv) < 1):
    print('Error: missing arguments!')
    print('e.g. python swc2nrrd.py neuron.swc Image.nrrd [scale]')
else:
    Iswc = str(sys.argv[1])
    Iout = str(sys.argv[2])
    
    if (len(sys.argv) < 2):    
      scale=np.int32(sys.argv[3])
      print(scale)
    
  
    print('Loading %s...'% (Iswc))
    with open(Iswc) as fI:
        swcIn = fI.readlines()
    
    lineDict = {}
    for thisLine in swcIn:
        if thisLine[0]!='#':
            splitLine = thisLine.split(" ")
            lineDict[int(splitLine[0])] = {'position':np.array([splitLine[2],splitLine[3],splitLine[4]],dtype=np.float),
                                      'radius':splitLine[5],
                                      'parent':int(splitLine[6])}
    maxExtent=[1000,1000,1000]
    
    for i in range(3):
            maxExtent[i] = np.max([(np.max([x['position'][i] for x in lineDict.values()])/scale).astype(np.int)])
            
    minExtent=[0,0,0]
    
    for i in range(3):
            minExtent[i] = np.min([(np.min([x['position'][i] for x in lineDict.values()])/scale).astype(np.int)])
    
    print(minExtent)
    print(maxExtent)
    
    outputImg = np.zeros(maxExtent,dtype=np.uint8)

    w = 3
    for thisDict in lineDict.values():
        p = np.round(np.divide(thisDict['position'],scale)).astype(np.int)
        outputImg[p[0]-w:p[0]+w+1,p[1]-w:p[1]+w+1,p[2]-w:p[2]+w+1]=np.uint8(255)    
    
    nrrd.write(Iout, np.uint8(outputImg[minExtent[0]:maxExtent[0],minExtent[1]:maxExtent[1],minExtent[2]:maxExtent[2]]))
    print('saved to ' + Iout)
