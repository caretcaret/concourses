#!/usr/local/bin/python

import glob
import os

RAW_PATH = './raw/course/'
PROCESSED_PATH = './processed/course/'
COURSE_DATA_PATTERN = '/*.html'

def scrape(raw_fname, processed_fname):
  try:
    pass
  except Exception as e:
    return False
  return True

def scrape_all(session_tags):
  for tag in session_tags:
    # make target directory if it doesn't exist
    directory = PROCESSED_PATH + tag
    if not os.path.exists(directory):
      os.makedirs(directory)

    # get all course html files
    filelist = glob.glob(RAW_PATH + tag + COURSE_DATA_PATTERN)
    count = 0
    total = len(filelist)
    for raw_fname in filelist:
      # naive filename manipulation
      processed_fname = raw_fname.replace(RAW_PATH, PROCESSED_PATH)
      processed_fname = processed_fname.replace('.html', '.json')
      success = scrape(raw_fname, processed_fname)
      if success:
        count += 1
        print("{} ({} of {})".format(processed_fname, count, total))
      else:
        print("{} unable to be scraped", raw_fname)
    return count

if __name__ == '__main__':
  session_tags = ['F13', 'S14', 'M14']
  scrape_all(session_tags)
