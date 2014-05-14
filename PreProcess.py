from numpy import unique, bincount, shape, min, max, sum, array, uint32, where, uint8, round
import nrrd
from matplotlib.pyplot import imshow, show, figure


def AutoBalance(data,threshold=0.00035,background=0):
    bins=unique(data)
    binc=bincount(data.flat)
    histogram=binc[binc>0]
    del binc
    if background in bins:
        i = where(bins==background)
        v = bins[i][0]
        c = histogram[i][0]
        th=int(((sum(histogram)-histogram[i][0])/shape(data)[2])*threshold)
    else:
        th=int((sum(histogram)/shape(data)[2])*threshold)
    m=min(bins)
    M=max(bins)
    for x in range(1,shape(bins)[0]-1):
        if sum(histogram[:x]) > th:
            m = x-1
            break
    for x in range(shape(bins)[0]-1,0,-1):
        if sum(histogram[x:]) > th:
            M = x
            break
    data[data>M]=M
    data[data<m]=m       
    dataA=round((data-m)*(255.0/(M-m)))
    return (dataA, array([m, M], dtype=uint32), array([bins,histogram],dtype=uint32)) 
    

data1, header1 = nrrd.read('/Volumes/Macintosh HD/Users/robertcourt/BTSync/usedtemplate.nrrd')
data1r, values, hist = AutoBalance(data1)
print values
        
data1, header1 = nrrd.read('/Volumes/Macintosh HD/Users/robertcourt/BTSync/engrailed_MARCM1_Fz-PP_BG-aligned.nrrd')
data1r, values, hist = AutoBalance(data1)

print values

im1=imshow(data1[:,:,130])
figure()
im2=imshow(data1r[:,:,130])
show()