#!/usr/local/bin/python

import re
import requests
import os, sys
import time
import io

INDEX_DIRECTORY = 'raw/index/'
COURSE_DIRECTORY = 'raw/course/'
COURSE_URL_PATTERN = 'https://enr-apps.as.cmu.edu/open/SOC/SOCServlet/courseDetails?COURSE={}&SEMESTER={}'
COURSE_URL_PATTERN_OLD = 'https://enr-apps.as.cmu.edu/open/SOC/SOCServlet/courseDetails?courseNo={}&SEMESTER={}'

class Session(object):
  def __init__(self, tag, name, indices):
    self.tag = tag
    self.name = name
    self.indices = indices
    directory = COURSE_DIRECTORY + self.tag + '/'
    if not os.path.exists(directory):
      os.makedirs(directory)

  def scrape_courses(self):
    self.courses = set()
    for index in self.indices:
      with open(INDEX_DIRECTORY + index) as f:
        for line in f:
          # naive check for course numbers: if the line begins with a
          # 5-digit number, it's a course
          match = re.search(r"(\d{5,5})", line)
          if match:
            self.courses.add(match.group(1))
    return self.courses

  def download_course_description(self, number):
    url = COURSE_URL_PATTERN.format(number, self.tag)
    # write file into cache
    path = COURSE_DIRECTORY + self.tag + '/' + str(number) + '.html'
    try:
      r = requests.get(url)
      with io.open(path, 'w', encoding='utf8') as f:
        f.write(r.text)
      return True
    except Exception as e:
      print(e)
      return False

f13 = Session('F13', "Fall 2013", ['sched_layout_fall_2013.dat'])
s14 = Session('S14', "Spring 2014", ['sched_layout_spring_2014.dat'])
m14 = Session('M14', "Summer 2014",
    ['sched_layout_summer_1_2014.dat', 'sched_layout_summer_2_2014.dat'])

if __name__ == '__main__':
  sessions = [f13, s14, m14]
  for session in sessions:
    session.scrape_courses()
    num_courses = len(session.courses)
    count = 0
    for course in session.courses:
      success = session.download_course_description(course)
      count += 1
      if success:
        print("{} ({} of {})".format(course, count, num_courses))
      else:
        print("Download failed:", course)

