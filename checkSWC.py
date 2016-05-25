import nrrd
import sys
import numpy as np

data, header = nrrd.read(str(sys.argv[2]))

lines = [line.strip() for line in open(str(sys.argv[1]))]

for line in lines:
    if '#' not in line:
        values = line.split(' ')
        xl = int(np.floor(np.floor(np.float(values[2])) / np.float(header['space directions'][0][0])))
        yl = int(np.floor(np.floor(np.float(values[3])) / np.float(header['space directions'][1][1])))
        zl = int(np.floor(np.floor(np.float(values[4])) / np.float(header['space directions'][2][2])))
        xh = int(np.ceil(np.ceil(np.float(values[2])) / np.float(header['space directions'][0][0]))+1)
        yh = int(np.ceil(np.ceil(np.float(values[3])) / np.float(header['space directions'][1][1]))+1)
        zh = int(np.ceil(np.ceil(np.float(values[4])) / np.float(header['space directions'][2][2]))+1)
        value = data[xl:xh, yl:yh, zl:zh]
        if np.sum(value) < 1:
            print(line)
            print(value)