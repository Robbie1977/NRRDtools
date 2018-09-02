import numpy as np
import sys, os
import nrrd

scale=1

if (len(sys.argv) < 2):
    print('Error: missing arguments!')
    print('e.g. python swc2nrrd.py template.nrrd neuron.swc Image.nrrd [scale]')
else:
    Itemp = str(sys.argv[1])
    Iswc = str(sys.argv[2])
    Iout = str(sys.argv[3])
    bounded = True
    
    if (len(sys.argv) < 3):    
      scale=np.int32(sys.argv[4])
      bounded = False
      
    
    print('Loading %s...'% (Itemp))
    tempData1, tempHeader1 = nrrd.read(Itemp)   
    
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
    extent=[1000,1000,1000]
    
    if bounded:
        for i in range(3):
            extent[i] = np.max([(np.max([x['position'][i] for x in lineDict.values()])/scale).astype(np.int),np.shape(tempData1)[i]])
    else:
        for i in range(3):
            extent[i] = (np.max([x['position'][i] for x in lineDict.values()])/scale).astype(np.int)
            
    print(extent)
    
    outputImg = np.zeros(extent,dtype=np.uint8)

    w = 3
    for thisDict in lineDict.values():
        p = np.round(np.divide(thisDict['position'],scale)).astype(np.int)
        outputImg[p[0]-w:p[0]+w+1,p[1]-w:p[1]+w+1,p[2]-w:p[2]+w+1]=np.uint8(255)

    nrrd.write(Iout, np.uint8(outputImg), header=tempHeader1)
    print('saved to ' + Iout)
