import tarfile
import os, sys

def untar(filename):
  print("Unpacking", filename)
  try:
    tar = tarfile.open(filename)
    tar.extractall()
    tar.close()
  except Exception as e:
    print("Extraction failed:", e)

def usage():
  print("Usage:\npython unpack.py raw\npython unpack.py processed")

if __name__ == '__main__':
  if len(sys.argv) < 2:
    usage()
  elif sys.argv[1].lower().strip() == 'raw':
    untar('raw.tgz')
  elif sys.argv[1].lower().strip() == 'processed':
    untar('processed.tgz')
  else:
    usage()
