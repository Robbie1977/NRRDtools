import numpy as np
import sys
import nrrd

# Check if the correct number of command-line arguments is provided
if len(sys.argv) < 2:
    print('Error: missing arguments!')
    print('e.g. python labelFillBetween.py image.nrrd [indexnumber]')
else:
    print('Processing {}...'.format(str(sys.argv[1])))
    data1, header1 = nrrd.read(str(sys.argv[1]))
    tv = 1
    if len(sys.argv) > 2:
        tv = np.uint8(sys.argv[2])
    print('Expanding index {}'.format(str(tv)))
    index1 = np.argwhere(data1 == tv)
    out1 = np.array(data1)
    print(np.histogram(data1, bins=np.unique(data1)))
    shp = np.shape(data1)
    skp = np.zeros([shp[0], shp[2]])
    for val in index1:
        if val[1] > skp[val[0], val[2]]:
            lst = index1[index1[:, 0] == val[0]]
            lst = lst[lst[:, 2] == val[2]]
            ep = np.max(lst[:, 1])
            if ep > val[1]:
                out1[val[0], val[1]:ep, val[2]] = tv
                skp[val[0], val[2]] = ep
    print(np.histogram(out1, bins=np.unique(out1)))
    for v in np.unique(data1[data1 > 0]):
        out1[data1 == v] = v
    nrrd.write('/Volumes/Macintosh HD/Users/robertcourt/BTSync/testout.nrrd', np.uint8(out1), options=header1)
    print(np.histogram(out1, bins=np.unique(out1)))
    print('done.')
