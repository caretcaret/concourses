from bottle import route, run, template, static_file
import os

DEVELOPMENT = True

@route('/')
def index():
  return template('index')

@route('/static/<filepath:path>')
def server_static(filepath):
  return static_file(filepath, root='./static')

run(host='localhost', port=int(os.environ.get("PORT", 8080)),
	reloader=DEVELOPMENT, debug=DEVELOPMENT)
