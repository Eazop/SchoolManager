from flask import Flask, request, session, g, redirect, url_for, abort, \
 render_template, flash
import datetime


from jinja2 import Template
import pymysql
import BPS

def Query(query):
    db = pymysql.connect(host='104.196.175.51', user='BPS', password='betterpowerschools', db='better_power_schools')
    cur = db.cursor()
    cur.execute(query)
    l = cur.fetchall()
    db.close()
    return l


app = Flask(__name__)

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
        if s.studentID != None:
            courses = s.courses
        elif t.teacherID != None:
            courses = t.currentCourses
        return render_template('teacherHome.html', courses = courses)


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
			ro = Query("SELECT studentID FROM students WHERE studentID=" + [request.form['username']])
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


			return redirect(url_for('loggedin'))
	return render_template('login.html', error=error)

@app.route('/loggedin', methods=['GET'])
def loggedin():
    error = None
    t.init(session['userid'])
    return render_template('loggedin.html', error = error)


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
	return render_template('AssignmentList.html', assignments = t.getAssignments())

@app.route('/Courses/<courseNum>', methods=['GET', 'POST'])
def assignmentCourse(courseNum):
        a = []
        assignments = Query("SELECT DISTINCT Title, Description, DueDate FROM assignments WHERE CourseID =" + str(courseNum))
        for assignment in assignments:
                temp = BPS.Assignment()
                temp.assignmentID = assignment[0]
                temp.description = assignment[1]
                temp.dueDate = assignment[2]
                a.append(temp)

        return render_template('Assignments.html', assignments = a, courseNum = courseNum)

@app.route('/Add', methods=['GET', 'POST'])
def assignmentAdd():
    courseNum = request.form['courseNum']

    t.submitAssignment(int(request.form['courseNum']),request.form['Title'], request.form['Description'], request.form['DueDate'])

    return redirect(url_for('assignmentCourse', courseNum = courseNum))

@app.route('/Courses/<courseNum>/<assignTitle>')
def List(courseNum, assignTitle):
    listID =[]
    nameList = []
    gradeList = []
    assignID = []
    x=0
    temp = Query("SELECT * FROM students WHERE Course1 =" + str(courseNum) +" OR Course2 =" + str(courseNum) +" OR Course3 =" + str(courseNum) +" OR Course4 =" + str(courseNum) +" OR Course5 =" + str(courseNum) +" OR Course6 = " + str(courseNum))
    for t in temp:
        listID.append(t[0])
        nameList.append(t[2] + " " + t[1])
        temp2 = Query("SELECT assignmentID, Grade FROM assignments WHERE StudentID =" + str(t[0]) + " AND Title = \"" + assignTitle + "\"")
        # assignID.append(temp2[0])
        gradeList.append(temp2[1]) if (len(temp2) == 2) else gradeList.append(None)
        x+=1
    # temp2 = Query("SELECT assignmentID, Grade FROM assignments WHERE CourseID =" + str(courseNum) + " AND Title = \"" + assignTitle)
    # for t in temp:
    #     l[0][x] = t
    return render_template('StudentAssignments.html', studentIDs = listID, nameList = nameList, gradeList = gradeList, assignID = assignID, total = x)

global t, s
t = BPS.Teacher()
s = BPS.Student()
if __name__ == '__main__':
	app.run(host='127.0.0.1', port=8080, debug=True)
