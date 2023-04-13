from numpy import unique, bincount, shape, min, max, sum, array, uint32, where, uint8, round
import nrrd
import sys
import os
from matplotlib.pyplot import imshow, show, figure


def AutoBalance(data, threshold=0.00035, background=0):
    bins = unique(data)
    binc = bincount(data.flat)
    histogram = binc[binc > 0]
    del binc

    if background in bins:
        i = where(bins == background)
        v = bins[i][0]
        c = histogram[i][0]
        th = int(((sum(histogram) - histogram[i][0]) / shape(data)[2]) * threshold)
    else:
        th = int((sum(histogram) / shape(data)[2]) * threshold)

    m = min(bins)
    M = max(bins)

    for x in range(1, shape(bins)[0] - 1):
        if sum(histogram[:x]) > th:
            m = x - 1
            break

    for x in range(shape(bins)[0] - 1, 0, -1):
        if sum(histogram[x:]) > th:
            M = x
            break

    data[data > M] = M
    data[data < m] = m
    dataA = round((data - m) * (255.0 / (M - m)))

    return (dataA, array([m, M], dtype=uint32), array([bins, histogram], dtype=uint32))


if len(sys.argv) < 2:
    print('e.g. python PreProcess.py image.nrrd output.nrrd')
else:
    fileName, fileExtension = os.path.splitext(sys.argv[1])
    if fileExtension == '.nrrd':
        data1, header1 = nrrd.read(sys.argv[1])
    elif fileExtension == '.lsm':
        # TBA using pylsm
        pass
