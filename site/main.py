from bottle import route, post, run, request, template, static_file, redirect, TEMPLATE_PATH
from pymongo import Connection
from bson import json_util
import os

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

@route('/data')
def data():
	if not request.json:
		return {}

	result = db.courses.find({'name': {'$regex': 'non-majors', '$options': 'i'}})
	return json_util.dumps({'courses': result})

@route('/static/<filepath:path>')
def server_static(filepath):
  return static_file(filepath, root=HERE+'/static')

run(host='localhost', port=int(os.environ.get("PORT", 8080)),
  server='cherrypy', reloader=DEVELOPMENT, debug=DEVELOPMENT)
