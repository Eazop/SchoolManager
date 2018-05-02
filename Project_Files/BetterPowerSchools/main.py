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

#URL for the dashboard; Cannot be accessed nless the user is already logged in, otherwise they will be prompted to log in
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

#Brings up the schedule for the student, including the teacher's name, id and course number
@app.route('/schedule', methods=['GET','POST'])
def Schedule():
    courses = p.student.courses
    teachers = []
    for course in courses:
        q = "SELECT TeacherID, Fname, Lname FROM  teachers WHERE Course1 = " + str(course.courseID) + " OR Course2 = " + str(course.courseID) + " OR Course3 = " + str(course.courseID) + " OR Course4 = " + str(course.courseID)
        teacher = Query(q)
        teachers.append(teacher)
    return render_template('schedule_student.html', courses = courses, teachers = teachers)

#The login screen that will query certain databases depending on the selection
#from the drop down menu
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

#Confirmation page for a successful loging; initializes the user's curent role
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

#Confirmation page for a successful logout
@app.route('/loggedout', methods=['GET'])
def loggedout():
	error = None
	return render_template('loggedout.html', error=error)

#Deconstructs the objects created during the session and pops the session
@app.route('/logout')
def logout():
    t.deconstruct()
    s.deconstruct()
    p.deconstruct()
    session.pop('userid', None)
    session.pop('logged_in', None)
    return redirect(url_for('loggedout'))

#Lists all the assignments for a teacher
@app.route('/Assignments')
def assignmentList():
	return render_template('AssignmentList.html', assignments = t.getAssignments())

#Lists all unique assignments for a given course
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

#Processing page for adding a new assignment to a course
@app.route('/Add', methods=['GET', 'POST'])
def assignmentAdd():
    courseNum = request.form['courseNum']

    t.submitAssignment(int(request.form['courseNum']),request.form['Title'], request.form['Description'], request.form['DueDate'])

    return redirect(url_for('assignmentCourse', courseNum = courseNum))

#Views all submissions for an assignment by the student's Name and ID
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

    return render_template('StudentAssignments.html', studentIDs = listID, nameList = nameList, gradeList = gradeList, assignID = assignID, total = x)

#The page to modify a given assignment. Everything can be changed
#Remember to add a calendar picker here
@app.route('/Courses/<courseNum>/<assignTitle>/Modify')
def Modify(courseNum, assignTitle):
    temp = Query("Select * FROM assignments WHERE Title =\"" + assignTitle + "\" AND courseID=" + str(courseNum))
    assignment = BPS.Assignment()
    assignment.init((int)(temp[0][0]), temp[0][1], temp[0][2], temp[0][3], temp[0][4], temp[0][5], temp[0][6])
    return render_template('ModifyAssignment.html', assignment = assignment, courseNum = courseNum)

#Processing page for the values taken in from the modify assignment function
#Returns the user to the assignments for the course
@app.route('/updating', methods=['GET', 'POST'])
def assignmentUpdate():
    courseNum = request.form['courseNum']
    title = request.form['origTitle']
    l = Query("UPDATE assignments SET title = \"" + request.form['Title'] + "\", dueDate = \"" + request.form['DueDate'] + "\", description = \"" + request.form['Description'] + "\" WHERE title = \""+ title + "\" AND CourseID =" + courseNum )
    return redirect(url_for('assignmentCourse', courseNum = courseNum))

#Processing page for deleting an assignment from the database and updating the
#page afterwards
@app.route('/Courses/<courseNum>/<assignTitle>/Delete')
def Delete(courseNum, assignTitle):
    temp = Query("DELETE FROM assignments WHERE CourseID=" + courseNum + " AND Title=\"" + assignTitle + "\"")

    return redirect(url_for('assignmentCourse', courseNum = courseNum))

#Returns the form to update a grade for an assignment
@app.route('/UpdateGrade/<assignmentID>')
def updateGradeHTML(assignmentID):
    return render_template("Grading.html", assignmentID=assignmentID)

#Processing page for updating the grade after submitting it
@app.route('/UpdatingGrade', methods=['GET', 'POST'])
def updateGrade():
    assignmentID = request.form['assignmentID']
    a = BPS.Assignment()
    a.initByID(assignmentID)
    a.updateGrade(request.form['Grade'])
    return redirect(url_for('List', courseNum =a.courseID, assignTitle=a.title))

#Processing page for sending a message
#Work in Progress
@app.route('/Sending', methods=['GET', 'POST'])
def sendMessage():
    message = BPS.Message()
    message.message = request.form['Message']
    message.teacherID = request.form['TeacherID']
    message.studentID = request.form['StudentID']
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d %H:%M")
    message.sendDate = date
    message.sendMessage()
    return redirect(url_for('messaging', teacherID = message.teacherID))

#Shows the unique conversations that a teacher may currently have
#Work in progress
@app.route("/Messages/<teacherID>")
def messaging(teacherID):
    q = "SELECT studentID FROM messages WHERE teacherID = " + TeacherID
    m = Query(q)
    a = []
    for ID in m:
        for stud in a:
            if stud.studentID != ID:
                student = BPS.Student()
                student.init(ID)
                a.append(student)
                break
    return render_template("MessageList.html", students=a, teacher = t)


global t, s, p
t = BPS.Teacher()
s = BPS.Student()
p = BPS.Parent()
if __name__ == '__main__':
	app.run(host='127.0.0.1', port=8080, debug=True)
