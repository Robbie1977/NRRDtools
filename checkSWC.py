import nrrd
import sys
import numpy as np

data, header = nrrd.read(str(sys.argv[2]))

lines = [line.strip() for line in open(str(sys.argv[1]))]

for line in lines:
    if '#' not in line:
        values = line.split(' ')
        x = np.float(values[2]) / np.float(header['space directions'][0][0])
        y = np.float(values[3]) / np.float(header['space directions'][1][1])
        z = np.float(values[4]) / np.float(header['space directions'][2][2])
        value = np.sum(data[
            np.floor(x):np.ceil(x)][
            np.floor(y):np.ceil(y)][
            np.floor(z):np.ceil(z)])
        if value < 1:
            print(line + ' = ' + str(value))
