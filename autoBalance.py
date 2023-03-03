import gc
import sys

import numpy as np

import nrrd

adjust_thresh = 0.0 #0.0035


def AutoBalance(data, threshold=adjust_thresh, background=0):
    """
    This function performs automatic intensity balancing on the input 3D data array.

    Args:
        data (ndarray): The input 3D data array to be balanced.
        threshold (float, optional): The threshold of maximum percentage of voxels that can be clipped.
        background (int, optional): The background level for intensity balancing.

    Returns:
        ndarray: The balanced 3D data array.
        dict: A dictionary containing the minimum and maximum intensity values of the balanced data.
        ndarray: The histogram of the input data.

    """
    try:
        threshold = float(threshold)
        if np.max(data) == 0:
            data = np.uint8(data)
        else:
            # scale to 8 bit
            data = np.uint8(np.round(255.0 * (np.double(data) / np.max(data))))
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
            th = np.long((np.sum(histogram[:mid]) - c) * threshold)
        else:
            th = np.long((np.sum(histogram[:mid])) * threshold)
        print('low end balancing:')
        print('number of background voxels: ' + str(c))
        print('number of data voxels: ' + str(np.sum(histogram[:mid]) - c))
        print('threshold set to: ' + str(th))
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
            print('number of low end voxels cut: ' +
                  str(np.sum(histogram[0:temp]) - c))
            # high end threshold only uses data from high end
            c = 0
            if background in bins[mid:]:
                i = np.where(bins == background)
                v = bins[i][0]
                c = histogram[i][0]
                th = np.long((np.sum(histogram[mid:]) - c) * threshold)
            else:
                th = np.long((np.sum(histogram[mid:])) * threshold)
            print('high end balancing:')
            print('number of background voxels: ' + str(c))
            print('number of data voxels: ' + str(np.sum(histogram[mid:]) - c))
            print('threshold set to: ' + str(th))
            for x in range(np.shape(bins)[0] - 1, 0, -1):
                if (np.sum(histogram[x:])) > th:
                    M = bins[x]
                    temp = x + 1
                    break
                if (x < 130):  # very low or no signal
                    M = np.uint8(255)
                    temp = np.uint8(255)
                    break
            print('number of high end voxels cut: ' +
                  str(np.sum(histogram[temp:])))
        del temp
        gc.collect()
        # if threshold is set to zero then force no BG clipping
        if threshold == 0:
            m = np.uint8(0)
            M = 255
        data[data > M] = M  # bring down outlyers to new max value
        # reduce the low noise to zero without reducing the remianing levels
        data[data < m] = m
        # scale levels to full 8 bit range
        dataA = np.round((data) * (255.0 / M))
        hist = np.zeros(255, dtype=np.long)
        for i in range(0, np.shape(bins)[0] - 1):
            hist[bins[i]] = histogram[i]
        return dataA, {'min': int(m), 'max': int(M)}, hist
    except Exception as e:
        print('Error during intensity auto balancing:')
        print(e)
        return data, {'min': int(0), 'max': int(255)}, np.zeros(255, dtype=np.long)


if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print('Error: missing arguments!')
        print(
            'e.g. python autoBalance.py imageIn.nrrd [imageOut.nrrd] [0] [0.0035]')
        print('0 = Background level')
        print(
            '0.0035 = adjustment threshold - max percentage of voxels that can be clipped')
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
        print('Loading input file %s...' % (str(sys.argv[1])))
        data, header = nrrd.read(str(sys.argv[1]))
        chan, Nbound, hist = AutoBalance(data, threshold=TH, background=BG)
        print('New boundaries %s' % (str(Nbound)))
        header['encoding'] = 'gzip'
        if 'space directions' in header.keys() and header['space directions'] == ['none', 'none', 'none']:
            header.pop("space directions", None)
        print('Saving result to %s...' % (outFile))
        nrrd.write(outFile, np.uint8(chan), header)
