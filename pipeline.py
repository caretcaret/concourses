#!/usr/local/bin/python

from __future__ import print_function
import re
import requests
import os, sys
import io
import bs4
import json

INDEX_RAW_DIRECTORY = 'raw/index/'
INDEX_PROCESSED_DIRECTORY = 'processed/index/'
COURSE_RAW_DIRECTORY = 'raw/course/'
COURSE_PROCESSED_DIRECTORY = 'processed/course/'
COURSE_URL_PATTERN = 'https://enr-apps.as.cmu.edu/open/SOC/SOCServlet/courseDetails?COURSE={}&SEMESTER={}'
SEARCH_FORM_URL = 'https://enr-apps.as.cmu.edu/open/SOC/SOCServlet/search'

class Index(object):
  def __init__(self, tag, force_download=False, force_scrape=False):
    self.tag = tag
    self.force_download = force_download
    self.force_scrape = force_scrape

    self.raw_directory = INDEX_RAW_DIRECTORY
    if not os.path.exists(self.raw_directory):
      os.makedirs(self.raw_directory)

    self.processed_directory = INDEX_PROCESSED_DIRECTORY
    if not os.path.exists(self.processed_directory):
      os.makedirs(self.processed_directory)

  def form_params(self):
    return {
      'SEMESTER': self.tag,
      'MINI': 'NO',
      'GRAD_UNDER': 'All',
      'PRG_LOCATION': 'All',
      'DEPT': 'All',
      'LAST_NAME': '',
      'FIRST_NAME': '',
      'BEG_TIME': 'All',
      'KEYWORD': '',
      'TITLE_ONLY': 'YES',
      'SUBMIT': ''
    }

  def download_search_results(self, outfile):
    try:
      r = requests.post(SEARCH_FORM_URL, data=self.form_params())
      with io.open(outfile, 'w', encoding='utf8') as f:
        f.write(r.text)
      return True
    except Exception as e:
      print(e)
      return False

  def scrape_search_results(self, infile, outfile):
    try:
      with io.open(infile, encoding='utf8') as f:
        results = f.read()

      # find all links with 5 digit numbers
      soup = bs4.BeautifulSoup(results)
      links = [link.get_text() for link in soup.find_all('a')]
      pattern = r"(\d{5,5})"
      courses = set(filter(lambda s: re.match(pattern, s), links))

      with open(outfile, 'w') as f:
        for course in courses:
          f.write(course + '\n')

      return len(courses)
    except Exception as e:
      print(e)
      return 0
  
  def parse_index(self, infile):
    try:
      with open(infile) as f:
        courses = f.read().strip().split()
      return courses
    except Exception as e:
      print(e)
      return []

  def get(self):
    raw_path = self.raw_directory + self.tag + '.html'
    processed_path = self.processed_directory + self.tag + '.txt'

    if self.force_download or not os.path.isfile(raw_path):
      if not self.download_search_results(raw_path):
        print("Could not download list of courses for", self.tag)
        return []

    if self.force_scrape or not os.path.isfile(processed_path):
      if not self.scrape_search_results(raw_path, processed_path):
        print("Could not scrape list of courses for", self.tag)
        return []

    return self.parse_index(processed_path)

class Course(object):
  def __init__(self, tag, number, force_download=False, force_scrape=False):
    self.tag = tag
    self.number = str(number)
    self.force_download = force_download
    self.force_scrape = force_scrape

    self.raw_directory = COURSE_RAW_DIRECTORY + self.tag + '/'
    if not os.path.exists(self.raw_directory):
      os.makedirs(self.raw_directory)

    self.processed_directory = COURSE_PROCESSED_DIRECTORY + self.tag + '/'
    if not os.path.exists(self.processed_directory):
      os.makedirs(self.processed_directory)

  def download_course(self, outfile):
    url = COURSE_URL_PATTERN.format(self.number, self.tag)
    try:
      r = requests.get(url)
      with io.open(outfile, 'w', encoding='utf8') as f:
        f.write(r.text)
      return True
    except Exception as e:
      print(e)
      return False

  def scrape_course(self, infile, outfile):
    try:
      with io.open(infile, encoding='utf8') as f:
        html = f.read()
      
      data = {'number': self.number}
      soup = bs4.BeautifulSoup(html)
      
      # course name
      info = soup.find(class_='with-data')
      name = info['data-maintitle']
      name = name.replace(self.number, '', 1).strip()
      data['name'] = name
      # session
      data['session'] = info['data-subtitle']
      # description
      description = soup.select('#course-detail-description > p')[0]
      contents = description.encode_contents()
      data['description'] = contents.decode(encoding='UTF-8')

      with io.open(outfile, 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False)
      return data
    except Exception as e:
      print(e)
      return False

  def parse_course(self, infile):
    try:
      with io.open(infile, encoding='utf8') as f:
        data = f.read()
      return json.loads(data)
    except Exception as e:
      print(e)
      return None

  def get(self):
    raw_path = self.raw_directory + self.number + '.html'
    processed_path = self.processed_directory + self.number + '.json'

    if self.force_download or not os.path.isfile(raw_path):
      if not self.download_course(raw_path):
        print("Could not download course", self.tag, self.number)
        return None

    if self.force_scrape or not os.path.isfile(processed_path):
      if not self.scrape_course(raw_path, processed_path):
        print("Could not scrape course", self.tag, self.number)
        return None

    return self.parse_course(processed_path)

def get_all(tags):
  num_tags = len(tags)
  for i, tag in enumerate(tags):
    index = Index(tag, force_download=False, force_scrape=False)
    print("{} ({} of {})".format(tag, i+1, num_tags))
    numbers = index.get()
    if not numbers:
      print("Error getting list of courses for", tag)
      continue
    
    num_courses = len(numbers)
    for j, number in enumerate(numbers):
      course = Course(tag, number, force_download=False, force_scrape=True)
      data = course.get()
      print("{} {} ({} of {})".format(tag, number, j+1, num_courses))
      if not data:
        print("Error getting data for", tag, number)

if __name__ == '__main__':
  tags = ['S06', 'M06', 'F06', 'S07', 'M07', 'F07', 'S08', 'M08', 'F08',
      'S09', 'M09', 'F09', 'S10', 'M10', 'F10', 'S11', 'M11', 'F11',
      'S12', 'M12', 'F12', 'S13', 'M13', 'F13', 'S14', 'M14']
  
  # get_all(tags)

  c = Course('S14', '15221', force_download=False, force_scrape=True).get()
  print(c)
