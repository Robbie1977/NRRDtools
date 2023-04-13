from PIL import Image
import numpy as np
import nrrd
import os, sys


def loadRaw(Ifile='./image.raw', Imode='L', Isize=(512,1024,185)):
  f = open(Ifile, 'rb')
  strData = f.read()
  f.close()
  Ssize = (Isize[0], (Isize[1] * Isize[2]))
  strip = Image.fromstring(Imode, Ssize, strData, 'raw')
  Rdata = np.reshape(strip, Isize[::-1])
  Idata = np.swapaxes(Rdata,0,-1)
  return Idata

def saveNRRD(Ifile='./image.nrrd', Idata=np.zeros((512,1024,185), dtype=np.uint8), Iheader={"type": "uint8", "dimension": 3, "encoding": "gzip"}):
  nrrd.write(str(Ifile), np.uint8(Idata), options=Iheader)
  return True


def convertRaw2NRRD(Ifile='./image.raw', template='./template.nrrd'):
  Nfile = str(Ifile).replace('.raw','.nrrd')
  data, header = nrrd.read(template)
  Tsize = np.shape(data)
  del data
  return saveNRRD(Nfile, loadRaw(Ifile, 'L', Tsize), header)


def convDirRaw2NRRD(folder='./', template='./template.nrrd'):
  for Ifile in os.listdir(folder):
    if '.raw' in Ifile:
      Nfile = str(Ifile).replace('.raw','.nrrd')
      if not os.path.exists(Nfile):
        print('converting ' + Ifile + ' to ' + Nfile + '...')
        convertRaw2NRRD(Ifile, template)

if __name__ == "__main__":
  if (len(sys.argv) < 3):
      print('Error: missing arguments!')
      print('e.g. python raw2NRRD.py rawFileDir template.nrrd')
  else:
      convDirRaw2NRRD(str(sys.argv[1]), str(sys.argv[2]))
