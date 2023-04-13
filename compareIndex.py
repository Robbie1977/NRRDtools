import png
import numpy as np
import sys, os, csv
import nrrd

# object pearson coefficent
def opc(d1,d2):
    Nd1 = np.squeeze(np.asarray(d1.flat,dtype=np.float128))
    Nd2 = np.squeeze(np.asarray(d2.flat,dtype=np.float128))

    th = 0

    Ta = np.add(Nd1, Nd2)
    Os = len([x for x in Ta if x > th])

    Na1 = np.divide(np.sum(Nd1),Os)
    Na2 = np.divide(np.sum(Nd2),Os)

    r=np.sum(np.multiply(np.subtract(Nd1,Na1),np.subtract(Nd2,Na2)))/np.sqrt(np.multiply(np.sum(np.square(np.subtract(Nd1,Na1))),np.sum(np.square(np.subtract(Nd2,Na2)))))

    return r

# overlap coefficient
def olc(d1,d2):
    Nd1 = np.squeeze(np.asarray(d1.flat,dtype=np.float128))
    Nd2 = np.squeeze(np.asarray(d2.flat,dtype=np.float128))

    # th = 0
    #
    # Ta = np.add(Nd1, Nd2)
    # Os = len([x for x in Ta if x > th])
    #
    # Na1 = np.divide(np.sum(Nd1),Os)
    # Na2 = np.divide(np.sum(Nd2),Os)

    r = np.sum(np.multiply(Nd1,Nd2))/np.sqrt(np.multiply(np.sum(np.square(Nd1)),np.sum(np.square(Nd2))))

    return r

def compare(data1, data2, result=None):
    if (data1.size != data2.size):
        print('\n\nError: Images must be the same size!!')
    else:
        results = []
        for i in np.unique(data1):
          if i > 0:
            test1 = np.zeros(np.shape(data1), dtype=np.uint8)
            test1[data1==i] = 1
            for k in np.unique(data2):
              if k > 0:
                test2 = np.zeros(np.shape(data2), dtype=np.uint8)
                test2[data2==k] = 1
                r1 = opc(test1,test2)
                r2 = olc(test1,test2)
                results = results + [(i,k,r1,r2)]
                print(str(i), str(k), str(r1), str(r2))
                if not result == None:
                  with open(result, 'a') as csvfile:
                    spamwriter = csv.writer(csvfile)
                    spamwriter.writerow([i,k,r1,r2])
    return results


if __name__ == "__main__":
  if (len(sys.argv) < 2):
      print('Error: missing arguments!')
      print('e.g. python compareIndex.py index1.nrrd index2.nrrd [results.csv]')
  else:
      print('Loading image: %s...'% (str(sys.argv[1])))
      data1, header1 = nrrd.read(str(sys.argv[1]))
      print('Loading image: %s...'% (str(sys.argv[2])))
      data2, header2 = nrrd.read(str(sys.argv[2]))
      resultfile=None
      if (len(sys.argv) > 2):
        resultfile = str(sys.argv[3])
      results = compare(data1, data2, result=resultfile)
