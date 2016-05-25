import nrrd
import sys
import numpy as np

data, header = nrrd.read(str(sys.argv[2]))

lines = [line.strip() for line in open(str(sys.argv[1]))]

for line in lines:
    if '#' not in line:
        values = line.split(' ')
        xl = np.floor(values[2]) / np.float(header['space directions'][0][0])
        yl = np.floor(values[3]) / np.float(header['space directions'][1][1])
        zl = np.floor(values[4]) / np.float(header['space directions'][2][2])
        xh = np.ceil(values[2]) / np.float(header['space directions'][0][0])
        yh = np.ceil(values[3]) / np.float(header['space directions'][1][1])
        zh = np.ceil(values[4]) / np.float(header['space directions'][2][2])
        value = np.sum(data[
            np.floor(xl):np.ceil(xh)][
            np.floor(yl):np.ceil(yh)][
            np.floor(zl):np.ceil(zh)])
        if value < 1:
            print(line + ' = ' + str(value))
