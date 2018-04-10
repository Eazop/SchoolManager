from flask import Flask, request, session, g, redirect, url_for, abort, \
 render_template, flash
 import BPSObjects

from jinja2 import Template
import pymysql

app = Flask(__name__)
t = None
app.config.update(dict(
DATABASE='',
SECRET_KEY='development key',
USERNAME='',
PASSWORD=''
))

def connect_db():
	db = pymysql.connect(host='104.196.175.51', user='BPS', password='betterpowerschools', db='better_power_schools')
	return db

@app.route('/', methods=['GET','POST'])
def home():
	db = pymysql.connect(host='104.196.175.51', user='BPS', password='betterpowerschools', db='better_power_schools')
	cur = db.cursor()
	cur.execute('SELECT * FROM teachers')
	teachers = cur.fetchall()
	return render_template('home.html', teachers=teachers)

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	db = pymysql.connect(host='104.196.175.51', user='BPS', password='betterpowerschools', db='better_power_schools')
	if request.method == 'POST':
		stringusername = None
		stringpassword = None

		role = request.form['role']

		curs = db.cursor()
		if (role == "teacher"):
			ro = curs.execute('SELECT TeacherID FROM teachers WHERE TeacherID=%s', [request.form['username']])
		elif (role == "student"):
			return "not implemented yet"
		elif (role == "parent"):
			return "not implemented yet"

		USERNAME = curs.fetchone()
		try:
			stringusername = ''.join(str([x for x in USERNAME]))
		except:
			print()

		curs = db.cursor()
		if (role == "teacher"):
			ro = curs.execute('SELECT TeacherID, Password FROM teachers WHERE TeacherID=%s and Password=%s', [request.form['username'], request.form['password']])
		elif (role == "student"):
			return "not implemented yet"
		elif (role == "parent"):
			return "not implemented yet"
		COMBINED = curs.fetchone()
		try:
			stringpassword = ''.join(str(COMBINED[1]))
		except:
			print()

		if str(request.form['username']) != stringusername[1]:
			error = 'Bad username'
			#flash(error)
		elif str(request.form['password']) != stringpassword:
			error = 'Bad password'
			#flash(error)
		else:
			session['logged_in'] = True
			session['userid'] = request.form['username']
			session['role'] = role
            t = Teacher()
            t.init(session['userid'])

			return redirect(url_for('loggedin'))
	return render_template('login.html', error=error)

@app.route('/loggedin', methods=['GET'])
def loggedin():
	error = None

	return render_template('loggedin.html', error=error)

@app.route('/loggedout', methods=['GET'])
def loggedout():
	error = None
	return render_template('loggedout.html', error=error)

@app.route('/logout')
def logout():
	session.pop('userid', None)
	session.pop('logged_in', None)
	return redirect(url_for('loggedout'))

#Example of creating a dynamic route. <name> is an argument
#that is passed to the function invoked by the route
@app.route('/name/<name>')
def get_name(name):
	return "Hello "+name

@app.route('/Assignments')
def assignmentList():
	return render_template('Assignments.html' assignmentList = t.getAssignments())


if __name__ == '__main__':
	app.run(host='127.0.0.1', port=8080, debug=True)
