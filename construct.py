"""Constructs the graph."""

from __future__ import print_function
from __future__ import unicode_literals
import os, sys
import io
import json
import glob
from collections import defaultdict

INDEX_RAW_DIRECTORY = 'raw/index/'
INDEX_PROCESSED_DIRECTORY = 'processed/index/'
COURSE_RAW_DIRECTORY = 'raw/course/'
COURSE_PROCESSED_DIRECTORY = 'processed/course/'
DEPARTMENTS_FILE = 'processed/departments.txt'
SITES_DATA_DIRECTORY = 'site/static/data/'

def parse_course(infile):
  try:
    with io.open(infile, encoding='utf8') as f:
      data = f.read()
    return json.loads(data)
  except Exception as e:
    print(e)
    return None

def flatten_prereqs(tree):
  ret = []
  for node in tree[1:]:
    if type(node) is list:
      ret.extend(flatten_prereqs(node))
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
    # so Tepper has this really weird thing where they have more graduate courses than fit
    # in one department number, so it spans 45, 46, 47, but we will give it a canonical number
    # of 45.
    # also, department 62 goes under four labels: CFA Interdisciplinary, BCA, BHA, BSA.
    # we will call this CFA (BXA is already taken by dept 52)
  depts.sort(key=lambda d: d['number'])
  return depts

def construct_graph(tags, out_dir, out_index_file):
  # make missing directories
  if not os.path.exists(out_dir):
    os.makedirs(out_dir)
  out_index_dir = os.path.dirname(out_index_file)
  if not os.path.exists(out_index_dir):
    os.makedirs(out_index_dir)
  
  depts = dept_info()
  for dept in depts:
    dept['count'] = 0
  indices = {dept['number']: i for i, dept in enumerate(depts)}
  # Tepper course numbers should map to the same index
  indices['46'] = indices['45']
  indices['47'] = indices['45']
  matrix = [[0] * len(depts) for i in range(len(depts))]
  dept_graphs = {number: {'nodes': {}, 'plinks': set(), 'clinks': set()} for number in indices}

  for tag in tags:
    for filename in glob.iglob(COURSE_PROCESSED_DIRECTORY + tag + '/*.json'):
      course = parse_course(filename)
      if course:
        number = course['number']
        dept = number[:2]
        # as far as I know, 74 has not been a real department since F10
        if dept == '74':
          continue
        # Tepper weirdness again!
        if dept == '46' or dept == '47':
          dept = '45'
        if number in dept_graphs[dept]['nodes']:
          dept_graphs[dept]['nodes'][number]['sessions'].append(tag)
        else:
          instance = {k: course[k] for k in ['number', 'units', 'name', 'prerequisites', 'corequisites']}
          instance['sessions'] = [tag]
          dept_graphs[dept]['nodes'][number] = instance
          dept_graphs[dept]['plinks'] |= set([(prereq, number) for prereq in flatten_prereqs(course['prerequisites'])])
          dept_graphs[dept]['clinks'] |= set([(coreq, number) for coreq in flatten_prereqs(course['corequisites'])])
          depts[indices[dept]]['count'] += 1

  for dept, graph in dept_graphs.items():
    graph['nodes'] = list(graph['nodes'].values())
    related = graph['plinks'] | graph['clinks']
    graph['plinks'] = [[p, n] for p, n in graph['plinks']]
    graph['clinks'] = [[c, n] for c, n in graph['clinks']]
    # count number of inter-department relations
    for other, number in related:
      matrix[indices[dept]][indices[other[:2]]] += 1

  try:
    with io.open(out_index_file, 'w') as f:
      s = json.dumps({'info': depts, 'adjacency': matrix}, ensure_ascii=False)
      f.write(s)

    if not os.path.exists(out_dir):
      os.makedirs(out_dir)

    for number in dept_graphs:
      with io.open(out_dir + number + '.json', 'w') as f:
        s = json.dumps(dept_graphs[number], ensure_ascii=False)
        f.write(s)
  except Exception as e:
    print(e)
    return False
  return True

if __name__ == '__main__':
  print("Preparing data files for website...")
  construct_graph(['F10', 'S11', 'M11', 'F11', 'S12', 'M12', 'F12', 'S13', 'M13', 'F13', 'S14', 'M14', 'F14'],
    './site/static/data/department/', './site/static/data/departments.json')
