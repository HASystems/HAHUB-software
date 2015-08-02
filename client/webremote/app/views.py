from flask import render_template
from app import app
import subprocess

@app.route('/')
def index():
	return render_template('home.html')

@app.route('/power')
def power():
	subprocess.call(["irsend", "SEND_ONCE", "westing", "KEY_POWER"])
	subprocess.call(["irsend", "SEND_ONCE", "westing", "KEY_POWER"])
	return render_template('power.html')

@app.route('/volumeup')
def volup():
	subprocess.call(["irsend", "SEND_ONCE", "westing", "KEY_VOLUMEUP"])
	return render_template('volumeup.html')

@app.route('/volumedown')
def voldown():
	subprocess.call(["irsend", "SEND_ONCE", "westing", "KEY_VOLUMEDOWN"])
	return render_template('volumedown.html')

