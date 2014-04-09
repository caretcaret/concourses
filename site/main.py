from __future__ import print_function
from bottle import route, post, run, request, template, static_file, redirect, TEMPLATE_PATH
from pymongo import Connection
from bson import json_util
import os
from functools import reduce
import re

DEVELOPMENT = True
HERE = os.path.dirname(os.path.realpath(__file__))
TEMPLATE_PATH.insert(0, HERE + '/views/')
DB_URL = 'mongodb://localhost:27017/'

connection = Connection(DB_URL)
db = connection.concourses

@route('/')
def home():
  return template('home')

@route('/courses')
@route('/courses/')
@route('/courses/<query:path>')
def courses(query=""):
  # query should be a comma separated list of departments, course
  # numbers, keywords, or ranges, possibly prefixed by "<session tag>/"
  # TODO: parse query and search
  return template('courses')

@post('/courses')
def search():
  # TODO: rewrite query into a get-url friendly link
  if request.forms.query:
    redirect('/courses/' + request.forms.query)
  redirect('/courses')

@route('/requirements')
def requirements():
  return template('requirements')

# serve this one file statically
@route('/data/departments')
def data_departments():
  return static_file('data/departments.json', root=HERE+'/static')

def item_map(item):
  if len(item) == 0:
    return {}
  # regex matching
  if re.match(r"^\d{2,2}$", item):
    # department
    return {'department': item}
  if re.match(r"^\d{5,5}$", item):
    # specific course
    return {'number': item}
  matchobj = re.match(r"^(\d\d)\-(\d\d\d)$", item)
  if matchobj:
    return {'number': matchobj.group(1) + matchobj.group(2)}
  return {'name': {'$regex': item, '$options': 'i'}}

def clause_map(clause):
  features = [item_map(item.strip()) for item in clause.split('&')]
  return reduce(lambda x, y: dict(list(x.items()) + list(y.items())), features)

def human_to_db(search):
  features = [clause_map(clause.strip()) for clause in search.strip().split(',')]
  return {'$query': {'$or': features}, '$orderby': {'number': 1}}


@post('/data')
def data():
  empty = json_util.dumps({'courses': []})
  search = request.json
  if type(search) is not str or len(search.strip()) == 0:
    return empty
  query = human_to_db(search)
  print(query)
  result = db.courses.find(query)
  return json_util.dumps({'courses': result})

@route('/static/<filepath:path>')
def server_static(filepath):
  return static_file(filepath, root=HERE+'/static')

run(host='localhost', port=int(os.environ.get("PORT", 8080)),
  server='tornado', reloader=DEVELOPMENT, debug=DEVELOPMENT)
