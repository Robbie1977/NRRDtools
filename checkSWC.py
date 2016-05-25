import nrrd
import sys
import numpy as np

data, header = nrrd.read(str(sys.argv[2]))

lines = [line.strip() for line in open(str(sys.argv[1]))]

for line in lines:
    if '#' not in line:
        values = line.split(' ')
        value = data[values[2] / np.float(header['space directions'][0][0])][
            values[3] / np.float(header['space directions'][1][1])][
            values[4] / np.float(header['space directions'][2][2])]
        if value < 1:
            print(values.join(',') + ' = ' + str(value))
