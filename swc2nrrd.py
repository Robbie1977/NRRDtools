import numpy as np
import sys, os
import nrrd

def sphere(shape, radius, position):
    # assume shape and position are both a 3-tuple of int or float
    # the units are pixels / voxels (px for short)
    # radius is a int or float in px
    semisizes = (radius,) * 3

    # genereate the grid for the support points
    # centered at the position indicated by position
    grid = [slice(-x0, dim - x0) for x0, dim in zip(position, shape)]
    position = np.ogrid[grid]
    # calculate the distance of all points from `position` center
    # scaled by the radius
    arr = np.zeros(shape, dtype=float)
    for x_i, semisize in zip(position, semisizes):
        arr += (np.abs(x_i / semisize) ** 2)
    # the inner part of the sphere will have distance below 1
    return arr <= 1.0


scale=1

if (len(sys.argv) < 2):
    print('Error: missing arguments!')
    print('e.g. python swc2nrrd.py template.nrrd neuron.swc Image.nrrd [width] [scale]')
else:
    Itemp = str(sys.argv[1])
    Iswc = str(sys.argv[2])
    Iout = str(sys.argv[3])
    bounded = True
    
    w = 0
    if (len(sys.argv) > 4):    
      w=np.int32(sys.argv[4])
     
    if (len(sys.argv) > 5):    
      scale=np.int32(sys.argv[5])
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

    r=0
    
    for thisDict in lineDict.values():
        p = np.round(np.divide(np.divide(thisDict['position'],[tempHeader1['space directions'][0][0],tempHeader1['space directions'][1][1],tempHeader1['space directions'][2][2]]),scale)).astype(np.int)
        
        if w==0 AND thisDict['radius']>0:
            r=thisDict['radius']
        else:
            r=w
        point = np.multiply(sphere(extent, r, p),np.uint8(255)).astype(np.uint8)
        outputImg = np.maximum(outputImg, point).astype(np.uint8)

    nrrd.write(Iout, np.uint8(outputImg), header=tempHeader1)
    print('saved to ' + Iout)
