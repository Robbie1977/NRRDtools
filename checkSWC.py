import nrrd
import sys
import numpy as np

data, header = nrrd.read(str(sys.argv[2]))

lines = [line.strip() for line in open(str(sys.argv[1]))]

for line in lines:
    if '#' not in line:
        values = line.split(' ')
        xl = np.floor(np.float(values[2])) / np.float(header['space directions'][0][0])
        yl = np.floor(np.float(values[3])) / np.float(header['space directions'][1][1])
        zl = np.floor(np.float(values[4])) / np.float(header['space directions'][2][2])
        xh = np.ceil(np.float(values[2])) / np.float(header['space directions'][0][0])
        yh = np.ceil(np.float(values[3])) / np.float(header['space directions'][1][1])
        zh = np.ceil(np.float(values[4])) / np.float(header['space directions'][2][2])
        value = data[
            np.floor(xl):np.ceil(xh)+1][
            np.floor(yl):np.ceil(yh)+1][
            np.floor(zl):np.ceil(zh)+1]
        if np.sum(value) < 1:
            print(line)
            print(value)
            print(str(xl) + ',' + str(xh))
            print(str(yl) + ',' + str(yh))
            print(str(zl) + ',' + str(zh))
            print(np.shape(data))