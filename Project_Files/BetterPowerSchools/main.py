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
    db.commit()
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
        teachers = []
        for course in courses:
            q = "SELECT TeacherID, Fname, Lname FROM  teachers WHERE Course1 = " + str(course.courseID) + " OR Course2 = " + str(course.courseID) + " OR Course3 = " + str(course.courseID) + " OR Course4 = " + str(course.courseID)
            teacher = Query(q)
            teachers.append(teacher)
        return render_template('studentHome.html', courses = courses, teachers = teachers)
    elif t.teacherID != None:
        courses = t.currentCourses
        return render_template('teacherHome.html', courses = courses)

    elif p.parentID != None:
        return render_template('parentHome.html')

    else:
        return render_template('login.html')

@app.route('/schedule', methods=['GET','POST'])
def Schedule():
    courses = p.courses
    teachers = []
    for course in courses:
        q = "SELECT TeacherID, Fname, Lname FROM  teachers WHERE Course1 = " + str(course.courseID) + " OR Course2 = " + str(course.courseID) + " OR Course3 = " + str(course.courseID) + " OR Course4 = " + str(course.courseID)
        teacher = Query(q)
        teachers.append(teacher)
    return render_template('schedule_student.html', courses = courses, teachers = teachers)

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
			ro = curs.execute('SELECT StudentID FROM students WHERE StudentID=%s', [request.form['username']])
		elif (role == "parent"):
		        ro = curs.execute('SELECT ParentID FROM parents WHERE ParentID=%s', [request.form['username']])


		USERNAME = curs.fetchone()
		try:
			stringusername = ''.join(str([x for x in USERNAME]))
		except:
			print()

		curs = db.cursor()
		if (role == "teacher"):
			ro = curs.execute('SELECT TeacherID, Password FROM teachers WHERE TeacherID=%s and Password=%s', [request.form['username'], request.form['password']])
		elif (role == "student"):
			ro = curs.execute('SELECT StudentID, Password FROM students WHERE StudentID=%s and Password=%s', [request.form['username'], request.form['password']])

		elif (role == "parent"):
			ro = curs.execute('SELECT ParentID, Password FROM parents WHERE ParentID=%s and Password=%s', [request.form['username'], request.form['password']])

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
    if session['role'] == "teacher":
        t.init(session['userid'])
    elif session['role'] == 'student':
        s.init(session['userid'])
    elif session['role'] == 'parent':
        p.init(session['userid'])


    return render_template('loggedin.html', error = error)


@app.route('/loggedout', methods=['GET'])
def loggedout():
	error = None
	return render_template('loggedout.html', error=error)

@app.route('/logout')
def logout():
    t.deconstruct()
    s.deconstruct()
    p.deconstruct()
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
                temp.title = assignment[0]
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
        assignID.append(temp2[0][0])
        gradeList.append(temp2[0][1])

        x+=1
    # temp2 = Query("SELECT assignmentID, Grade FROM assignments WHERE CourseID =" + str(courseNum) + " AND Title = \"" + assignTitle)
    # for t in temp:
    #     l[0][x] = t
    return render_template('StudentAssignments.html', studentIDs = listID, nameList = nameList, gradeList = gradeList, assignID = assignID, total = x)

@app.route('/Courses/<courseNum>/<assignTitle>/Modify')
def Modify(courseNum, assignTitle):
    temp = Query("Select * FROM assignments WHERE Title =\"" + assignTitle + "\" AND courseID=" + str(courseNum))
    assignment = BPS.Assignment()
    assignment.init((int)(temp[0][0]), temp[0][1], temp[0][2], temp[0][3], temp[0][4], temp[0][5], temp[0][6])
    return render_template('ModifyAssignment.html', assignment = assignment, courseNum = courseNum)

@app.route('/updating', methods=['GET', 'POST'])
def assignmentUpdate():
    courseNum = request.form['courseNum']
    title = request.form['origTitle']
    l = Query("UPDATE assignments SET title = \"" + request.form['Title'] + "\", dueDate = \"" + request.form['DueDate'] + "\", description = \"" + request.form['Description'] + "\" WHERE title = \""+ title + "\" AND CourseID =" + courseNum )
    return redirect(url_for('assignmentCourse', courseNum = courseNum))

@app.route('/Courses/<courseNum>/<assignTitle>/Delete')
def Delete(courseNum, assignTitle):
    temp = Query("DELETE FROM assignments WHERE CourseID=" + courseNum + " AND Title=\"" + assignTitle + "\"")

    return redirect(url_for('assignmentCourse', courseNum = courseNum))

@app.route('/UpdateGrade/<assignmentID>')
def updateGradeHTML(assignmentID):
    return render_template("Grading.html", assignmentID=assignmentID)

@app.route('/UpdatingGrade', methods=['GET', 'POST'])
def updateGrade():
    assignmentID = request.form['assignmentID']
    a = BPS.Assignment()
    a.initByID(assignmentID)
    print("Not updated grade")
    a.updateGrade(request.form['Grade'])
    print("Updated Grade")
    return redirect(url_for('List', courseNum =a.courseID, assignTitle=a.title))

global t, s, p
t = BPS.Teacher()
s = BPS.Student()
p = BPS.Parent()
if __name__ == '__main__':
	app.run(host='127.0.0.1', port=8080, debug=True)
