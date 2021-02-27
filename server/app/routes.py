from flask import render_template, send_from_directory, send_file, Response
from app import app
# Load routes from modules in "controllers" directory
from app.controllers import *
from app.czml import get_czml

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/favicon.png')
def favicon():
    return send_file('favicon.png')

@app.route('/data/<path:path>')
def send_js(path):
    return send_from_directory('/home/thomson/devel/aquarius/server/data', path)


@app.route('/czml/<id>')
def send_viewer(id):

    return Response(get_czml(id), mimetype="application/json")

