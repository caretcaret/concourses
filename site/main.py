from __future__ import print_function
from bottle import route, post, run, request, template, static_file, redirect, TEMPLATE_PATH
from pymongo import MongoClient
from bson import json_util
import os
from functools import reduce
import re
try:
  from urllib.parse import urlparse
except ImportError:
  from urlparse import urlparse

DEVELOPMENT = True
HERE = os.path.dirname(os.path.realpath(__file__))
TEMPLATE_PATH.insert(0, HERE + '/views/')
DB_URL = os.environ.get('MONGOLAB_URI', 'mongodb://localhost:27017/concourses')

parsed_db_url = urlparse(DB_URL)
DB_USERNAME = parsed_db_url.username
DB_PASSWORD = parsed_db_url.password

DB_ADDR, DB_NAME = DB_URL.rsplit('/', 1)

client = MongoClient(DB_URL)
db = client[DB_NAME]
if DB_USERNAME and DB_PASSWORD:
  db.authenticate(DB_USERNAME, DB_PASSWORD)

@route('/')
def home():
  return template('home')

@route('/evaluation')
def evaluation():
  return template('eval')

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
    return None
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
  return {'name': {'$regex': re.escape(item), '$options': 'i'}}

def clause_map(clause):
  features = [item_map(item.strip()) for item in clause.split('&')]
  features = [feature for feature in features if feature]
  if len(features) == 0:
    return None
  return {'$and': features}

def human_to_db(search):
  features = [clause_map(clause.strip()) for clause in search.strip().split(',')]
  features = [feature for feature in features if feature]
  if len(features) == 0:
    return None
  return {'$query': {'$or': features}, '$orderby': {'number': 1}}


@post('/data/details')
def data_details():
  """Fetch all instances for a course number."""
  empty = json_util.dumps({'instances': []})
  search = request.json
  if type(search) is not str or len(search.strip()) == 0:
    return empty
  query = {'number': search}
  print("Details fetch:", query)
  result = db.instances.find(query)
  return json_util.dumps({'instances': result})

@post('/data')
def data():
  empty = json_util.dumps({'courses': []})
  search = request.json
  if type(search) is not str or len(search.strip()) == 0:
    return empty
  query = human_to_db(search)
  print("List search:", query)
  if not query:
    return empty
  result = db.courses.find(query)
  return json_util.dumps({'courses': result})

@route('/static/<filepath:path>')
def server_static(filepath):
  return static_file(filepath, root=HERE+'/static')

run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)),
  server='tornado', reloader=DEVELOPMENT, debug=DEVELOPMENT)
