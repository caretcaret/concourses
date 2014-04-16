"""
Populates the MongoDB database with courses.
Creates the json file for departments.
"""

from __future__ import print_function, unicode_literals
import pymongo
import io
import json
import glob
import os

INDEX_RAW_DIRECTORY = 'raw/index/'
INDEX_PROCESSED_DIRECTORY = 'processed/index/'
COURSE_RAW_DIRECTORY = 'raw/course/'
COURSE_PROCESSED_DIRECTORY = 'processed/course/'
DEPARTMENTS_FILE = 'processed/departments.txt'
DEPARTMENTS_OUTPUT_FILE = 'site/static/data/departments.json'

def parse_offering(infile):
  try:
    with io.open(infile, encoding='utf8') as f:
      data = f.read()
    return json.loads(data)
  except Exception as e:
    print(e)
    return None

def flatten_reqs(tree):
  ret = []
  for node in tree[1:]:
    if type(node) is list:
      ret.extend(flatten_reqs(node))
    else:
      ret.append(node)
  return ret

def dept_info():
  depts = []
  with io.open(DEPARTMENTS_FILE, 'r', encoding='utf8') as f:
    departments = [line.strip() for line in f.read().strip().split('\n')]
  for department in departments:
    number, code, name = department.split(' ', 2)
    depts.append({'number': number, 'code': code, 'name': name})
  # so Tepper has this really weird thing where they have more graduate
  # courses than fit in one department number, so it spans 45, 46, 47, but
  # we will give it a canonical number of 45.
  # also, department 62 goes under four names; we will call it CFA
  depts.sort(key=lambda d: d['number'])
  return depts

def offering_generator(tags):
  for tag in tags:
    for filename in glob.iglob(COURSE_PROCESSED_DIRECTORY + tag + '/*.json'):
      offering = parse_offering(filename)
      if not offering:
        continue
        
      number = offering['number']
      dept = number[:2]
      # Tepper weirdness
      if dept in ['46', '47']:
        dept = '45'
      course = {k: v for k, v in offering.items() if k in
          ['corequisites', 'prerequisites', 'crosslisted', 'description',
            'mini', 'name', 'notes', 'number', 'permission', 'units',
            'urls']}
      course['department'] = dept
      instance = {k: v for k, v in offering.items() if k in
          ['reservations', 'session', 'lectures', 'number']}
      instance['tag'] = tag

      yield (tag, number, course, instance)

def main(tags, dept_outfile, dburl='mongodb://localhost:27017/'):
  client = pymongo.MongoClient(dburl)
  db = client.concourses
  courses_coll = db.courses
  instances_coll = db.instances

  # setup cross department matrix
  depts = dept_info()
  for dept in depts:
    dept['count'] = 0
  seen = set()
  indices = {dept['number']: i for i, dept in enumerate(depts)}
  # Tepper weirdness
  indices['46'] = indices['45']
  indices['47'] = indices['45']
  matrix = [[0] * len(depts) for i in range(len(depts))]

  offerings = offering_generator(tags)
  courses = {}
  instances = {}
  for tag, number, course, instance in offerings:
    if number not in seen:
      seen.add(number)
      dept = number[:2]
      depts[indices[dept]]['count'] += 1
      for req in flatten_reqs(course['prerequisites']) + flatten_reqs(course['corequisites']):
        matrix[indices[dept]][indices[req[:2]]] += 1
      courses[number] = course
    instances[number, tag] = instance

  # write to db
  db.drop_collection(courses_coll)
  db.drop_collection(instances_coll)
  courses_coll.insert(courses.values())
  instances_coll.insert(instances.values())
  
  # output the adjacency matrix
  dirname = os.path.dirname(os.path.abspath(dept_outfile))
  if not os.path.isdir(dirname):
    os.path.makedirs(dirname)
  try:
    with io.open(dept_outfile, 'w') as f:
      s = json.dumps({'info': depts, 'adjacency': matrix}, ensure_ascii=False)
      f.write(s)
  except Exception as e:
    print(e)
    return False
  return True

if __name__ == '__main__':
  main(['S13', 'M13', 'F13', 'S14', 'M14', 'F14'], DEPARTMENTS_OUTPUT_FILE)
