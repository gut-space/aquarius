from flask import render_template
from app import app
from app import obslist
from app import obs

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")
@app.route('/favicon.png')
def favicon():
    return send_file('favicon.png')
