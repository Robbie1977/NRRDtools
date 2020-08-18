import numpy as np
import sys, os
import nrrd

def sphere(shape, radius, position):
    # assume shape and position are both a 3-tuple of int or float
    # the units are pixels / voxels (px for short)
    # radius is a int or float in px
    semisizes = (radius,) * 3

    #ignore divide by zero
    np.seterr(divide='ignore', invalid='ignore') 
    
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
    print('e.g. python swc2nrrd.py template.nrrd neuron.swc Image.nrrd [width] [scale] [Xoffset,Yoffset,Zoffset]')
else:
    Itemp = str(sys.argv[1])
    Iswc = str(sys.argv[2])
    Iout = str(sys.argv[3])
    offset = [0.0,0.0,0.0]
    bounded = True
    
    w = 0
    if (len(sys.argv) > 4):    
      w=np.int32(sys.argv[4])
     
    if (len(sys.argv) > 5):    
      scale=np.float(sys.argv[5])
      bounded = False

    if (len(sys.argv) > 6):    
      offset=np.float(sys.argv[6].split(','))
     
    
    print('Loading %s...'% (Itemp))
    tempData1, tempHeader1 = nrrd.read(Itemp)   
    
    print('Loading %s...'% (Iswc))
    with open(Iswc) as fI:
        swcIn = fI.readlines()
    
    lineDict = {}
    for thisLine in swcIn:
        if thisLine[0]!='#':
            splitLine = thisLine.split(" ")
            lineDict[int(splitLine[0])] = {'position':np.array([np.float(splitLine[2])+offset[0],np.float(splitLine[3])+offset[1],np.float(splitLine[4])+offset[2]],dtype=np.float),
                                      'radius':splitLine[5],
                                      'parent':int(splitLine[6])}
    
    extent=tempHeader1['sizes']

    print(extent)

    outputImg = np.zeros(extent,dtype=np.uint8)


    r=0
    
    for thisDict in lineDict.values():
        r=w
        p = np.clip(np.floor(np.divide(np.divide(thisDict['position'],[tempHeader1['space directions'][0][0],tempHeader1['space directions'][1][1],tempHeader1['space directions'][2][2]]),scale)),[0,0,0],np.subtract(extent,1)).astype(np.int)
        if thisDict['radius'] != "NA" AND np.divide(float(thisDict['radius']),scale)>r:
            r=np.divide(float(thisDict['radius']),scale)
        if r<1:
            outputImg[p[0],p[1],p[2]]=np.uint8(255)
        else:
            point = np.multiply(sphere(extent, r, p),np.uint8(255)).astype(np.uint8)
            outputImg = np.maximum(outputImg, point).astype(np.uint8)

    nrrd.write(Iout, np.uint8(outputImg), header=tempHeader1)
    print('saved to ' + Iout)
