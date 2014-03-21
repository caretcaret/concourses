"""Constructs the graph."""

from __future__ import print_function
import os, sys
import io
import json
import glob

INDEX_RAW_DIRECTORY = 'raw/index/'
INDEX_PROCESSED_DIRECTORY = 'processed/index/'
COURSE_RAW_DIRECTORY = 'raw/course/'
COURSE_PROCESSED_DIRECTORY = 'processed/course/'


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

def construct_graph(outfile):
  graph = {'nodes': dict(), 'links': set()}

  for filename in glob.iglob(COURSE_PROCESSED_DIRECTORY + '*/*.json'):
    course = parse_course(filename)
    if course:
      number = course['number']
      if number in graph['nodes']:
        graph['nodes'][number]['sessions'].append(course['session'])
      else:
        instance = {k: course[k] for k in ['number', 'units', 'name']}
        instance['sessions'] = [course['session']]
        graph['nodes'][number] = instance
        graph['links'] |= set([(number, prereq) for prereq in flatten_prereqs(course['prerequisites'])])
        graph['links'] |= set([(number, coreq) for coreq in flatten_prereqs(course['corequisites'])])

  graph['nodes'] = list(graph['nodes'].values())
  for node in graph['nodes']:
    total = len(node['sessions'])
    fall = len([s for s in node['sessions'] if s.startswith("Fall")])
    spring = len([s for s in node['sessions'] if s.startswith("Spring")])
    node['sessions'] = [1.0 * fall / total, 1.0 * spring / total]
  graph['links'] = [[n, p] for n, p in graph['links']]

  # write json
  try:
    with io.open(outfile, 'w', encoding='utf8') as f:
      json.dump(graph, f, ensure_ascii=False)
  except Exception as e:
    print(e)
    return False

if __name__ == '__main__':
  construct_graph('./site/static/data/graph.json')
