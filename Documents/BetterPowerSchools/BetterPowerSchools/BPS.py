import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template,flash
import pymysql

app = Flask(__name__) #create the application instance
db= pymysql.connect("104.196.175.51", "BPS","betterpowerschools", "better_power_schools")
app.config.from_object(__name__) #load config from this file, flaskr.py
c =  db.cursor()

#Load default config and override config from an environment variable
app.config.update(dict(
	db = pymysql.connect("104.196.175.51", "BPS","betterpowerschools", "better_power_schools"),
	SECRET_KEY='development key',
	USERNAME='admin',
	PASSWORD='default'
))
app.config.from_envvar('BPS_SETTINGS', silent=True)

@app.route('/')
def show_entries():
	cur = c.execute('select * from teachers')
	entries = cur.fetchall()
	return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
	if not session.get('logged_in'):
		abort(401)
	c.execute('insert into teachers (fname, lname) values (?, ?)',
		[request.form['title'], request.form['text']])
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('You were logged in')
			return redirect(url_for('show_entries'))
	return renger_template('login.html', error=error)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('you were logged out')
	return redirect(url_for('show entries'))
