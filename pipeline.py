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
    have_download = os.path.isfile(raw_path)
    have_processed = os.path.isfile(processed_path)

    if self.force_download or not have_download and not have_processed:
      if not self.download_search_results(raw_path):
        print("Could not download list of courses for", self.tag)
        return []

    if self.force_scrape or not have_processed:
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

  @classmethod
  def parse_prereqs(cls, prereqs):
    return prereqs

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
      contents = contents.decode(encoding='UTF-8')
      data['description'] = re.sub(r"\s+", ' ', contents)
      # dd/dt pairs
      terms = soup('dt')
      for term in terms:
        definition = term.find_next_sibling('dd')
        if definition:
          label = term.string.strip()
          value = definition.encode_contents()
          value = value.decode(encoding='UTF-8').strip()
          if label == 'Prerequisites':
            data['prerequisites'] = self.parse_prereqs(value) # todo: tree
          elif label == 'Corequisites':
            if value == 'None':
              data['corequisites'] = []
            else:
              data['corequisites'] = [s.strip() for s in value.split(' , ')]
          elif label == 'Notes':
            data['notes'] = re.sub(r"\s+", ' ', value)
          elif label == 'Cross-Listed Courses':
            if value == 'None':
              data['crosslisted'] = []
            else:
              data['crosslisted'] = [s.strip() for s in value.split(' , ')]
          elif label == 'Special Permission Required':
            data['permission'] = value == 'Yes'
          elif label == 'Related URLs':
            data['urls'] = [a['href'] for a in definition('a')]
          else:
            print("Unused term", label, value)
      # schedule table is the first table
      schedule_rows = soup.find('table').find('tbody').find_all('tr')
      # if the table has a sessions column, shift over things by one
      schedule_header = soup.find('table').find('thead').find_all('th')
      if schedule_header[1].string == 'Session':
        session = 1
      else:
        session = 0
      # sticky state for lecture categorization
      lecture = ''
      section = ''
      data['lectures'] = {}
      for i, row in enumerate(schedule_rows):
        cells = row.find_all('td')
        # units are only available in the first row
        if i == 0:
          # may be a range, csv, or 'VAR'
          data['units'] = cells[1+session].string.strip()
          data['mini'] = bool(cells[3+session].string)
        
        next_lecture = cells[2+session].string
        if next_lecture:
          if not lecture or not lecture.startswith('Lec'):
            lecture = next_lecture.strip()
          else:
            if next_lecture.startswith('Lec'):
              lecture = next_lecture.strip()
        next_section = cells[2+session].string
        if next_section and next_section.strip():
          section = next_section.strip()

        if lecture not in data['lectures']:
          data['lectures'][section] = {'meetings': []}

        meeting = {}
        meeting['cancelled'] = bool(cells[0].string)
        if session:
          if cells[1].string:
            meeting['session'] = cells[1].string.strip()
        days = cells[4+session]
        meeting['days'] = list(cells[4+session].stripped_strings)[0]
        meeting['begin'] = list(cells[5+session].stripped_strings)[0]
        meeting['end'] = list(cells[6+session].stripped_strings)[0]
        meeting['campus'] = list(cells[7+session].stripped_strings)[0]
        meeting['room'] = list(cells[8+session].stripped_strings)[0]
        instructors = cells[9+session]('li')
        if instructors:
          meeting['instructors'] = [ins.string.strip() for ins in instructors]
        else:
          meeting['instructors'] = cells[9+session].find('em').string.strip()
        if lecture == section:
          data['lectures'][lecture]['meetings'].append(meeting)
        else:
          if 'recitations' not in data['lectures'][lecture]:
            data['lectures'][lecture]['recitations'] = {}
          if section not in data['lectures'][lecture]['recitations']:
            data['lectures'][lecture]['recitations'][section] = {'meetings': []}
          data['lectures'][lecture]['recitations'][section]['meetings'].append(meeting)

      # parse reservations
      reservations = soup.find('h4', text='Reservations').parent
      rtable = reservations.find('table')
      data['reservations'] = {}
      if rtable:
        rows = rtable('tr')
        for row in rows[1:]:
          cells = row('td')
          section = cells[0].string.strip()
          if section not in data['reservations']:
            data['reservations'][section] = []
          department = cells[1].string.strip()
          department = department.replace('Some reservations are for', '')
          department = re.sub(r"\s+", ' ', department)
          data['reservations'][section].append(department.strip())
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
    have_download = os.path.isfile(raw_path)
    have_processed = os.path.isfile(processed_path)

    if self.force_download or not have_download and not have_processed:
      if not self.download_course(raw_path):
        print("Could not download course", self.tag, self.number)
        return None

    if self.force_scrape or not have_processed:
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

  #get_all(tags)

  tests = [('S14', '15221'), ('F13', '99101'), ('F13', '15210'), ('F13', '76101'), ('S14', '15112'), ('F13', '82135'), ('S14', '10601'), ('S14', '15214')]
  for tag, course in tests:
    c = Course(tag, course, force_scrape=True).get()
    print(json.dumps(c, indent=4))
