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
    
    if (len(sys.argv) < 3):    
      scale=np.int32(sys.argv[4])
    
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
    
    for i in range(3):
        extent[i] = np.max([(np.max([x['position'][i] for x in lineDict.values()])/100).astype(np.int),np.shape(tempData1)[i]])
        
    print(extent)
    
    outputImg = np.zeros(extent)

    w = 3
    for thisDict in lineDict.values():
        p = np.round(np.divide(thisDict['position'],100)).astype(np.int)
        outputImg[p[0]-w:p[0]+w+1,p[1]-w:p[1]+w+1,p[2]-w:p[2]+w+1]=255

    nrrd.write(Iout, outputImg, options=tempHeader1)
    print('saved to ' + Iout)
