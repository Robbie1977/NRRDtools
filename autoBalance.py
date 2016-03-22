import gc
import sys

import numpy as np

import nrrd

adjust_thresh = 0.0035


def AutoBalance(data, threshold=adjust_thresh, background=0):
    try:
        threshold = float(threshold)
        if np.max(data) == 0:
            data = np.uint8(data)
        else:
            data = np.uint8(np.round(255.0 * (np.double(data) / np.max(data))))  # scale to 8 bit
        bins = np.unique(data)
        binc = np.bincount(data.flat)
        histogram = binc[binc > 0]
        del binc
        gc.collect()
        temp = 1
        c = 0
        mid = int(np.round(np.shape(bins)[0] / 2.0))
        # low end threshold only uses data from low end
        if background in bins[:mid]:
            i = np.where(bins == background)
            v = bins[i][0]
            c = histogram[i][0]
            th = long((np.sum(histogram[:mid]) - c) * threshold)
        else:
            th = long((np.sum(histogram[:mid])) * threshold)
        print 'low end balancing:'
        print 'number of background voxels: ' + str(c)
        print 'number of data voxels: ' + str(np.sum(histogram[:mid]) - c)
        print 'threshold set to: ' + str(th)
        m = np.min(bins)
        M = np.max(bins)
        if M == m:
            m = np.uint8(0)
            M = np.uint8(255)
        else:
            for x in range(1, np.shape(bins)[0] - 1):
                if (np.sum(histogram[0:x]) - c) > th:
                    m = bins[x - 1]
                    temp = x - 1
                    break
            print 'number of low end voxels cut: ' + str(np.sum(histogram[0:temp]) - c)
            # high end threshold only uses data from high end
            c = 0
            if background in bins[mid:]:
                i = np.where(bins == background)
                v = bins[i][0]
                c = histogram[i][0]
                th = long((np.sum(histogram[mid:]) - c) * threshold)
            else:
                th = long((np.sum(histogram[mid:])) * threshold)
            print 'high end balancing:'
            print 'number of background voxels: ' + str(c)
            print 'number of data voxels: ' + str(np.sum(histogram[mid:]) - c)
            print 'threshold set to: ' + str(th)
            for x in range(np.shape(bins)[0] - 1, 0, -1):
                if (np.sum(histogram[x:])) > th:
                    M = bins[x]
                    temp = x + 1
                    break
            print 'number of high end voxels cut: ' + str(np.sum(histogram[temp:]))
        del temp
        gc.collect()
        # if threshold is set to zero then force no BG clipping
        if threshold == 0:
            m = np.min(data)
        data[data > M] = M
        data[data < m] = m
        dataA = np.round((data - m) * (255.0 / (M - m)))
        hist = np.zeros(255, dtype=long)
        for i in range(0, np.shape(bins)[0] - 1):
            hist[bins[i]] = histogram[i]
        return dataA, {'min': int(m), 'max': int(M)}, hist
    except Exception, e:
        print 'Error during intensity auto balancing:'
        print (e)
        return data, {'min': int(0), 'max': int(255)}, np.zeros(255, dtype=long)

if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print 'Error: missing arguments!'
        print 'e.g. python autoBalance.py imageIn.nrrd [imageOut.nrrd] [0] [0.0035]'
        print '0 = Background level'
        print '0.0035 = adjustment threshold - max percentage of voxels that can be clipped'
    else:
        outFile = str(sys.argv[1])
        if (len(sys.argv) > 2):
            outFile = str(sys.argv[2])
        BG = 0
        if (len(sys.argv) > 3):
            BG = int(sys.argv[3])
        TH = adjust_thresh
        if (len(sys.argv) > 4):
            TH = float(sys.argv[4])
        print 'Loading input file %s...' % (str(sys.argv[1]))
        data, header = nrrd.read(str(sys.argv[1]))
        chan, Nbound, hist = AutoBalance(data, threshold=TH, background=BG)
        print 'New boundaries %s' % (str(Nbound))
        print 'Saving result to %s...' % (outFile)
        nrrd.write(outFile, np.uint8(chan), options=header)
