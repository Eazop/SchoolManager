from flask import Flask, request, session, g, redirect, url_for, abort, \
 render_template, flash
import datetime


from jinja2 import Template
import pymysql
import BPS

#Just queries the database for whatever information you give it
#NOTE: It returns a tuple since it is a fetchall
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

#Dashboard for the application
#For a student it will find information for their teachers and courses, then list them
#For a teacher it will list the courses that they teach
#For a parent it will find information for the parent's child's classes and teachers
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

#Shows a schedule for a student
@app.route('/schedule', methods=['GET','POST'])
def Schedule():
    courses = p.courses
    teachers = []
    for course in courses:
        q = "SELECT TeacherID, Fname, Lname FROM  teachers WHERE Course1 = " + str(course.courseID) + " OR Course2 = " + str(course.courseID) + " OR Course3 = " + str(course.courseID) + " OR Course4 = " + str(course.courseID)
        teacher = Query(q)
        teachers.append(teacher)
    return render_template('schedule_student.html', courses = courses, teachers = teachers)

#Handles login in requests and queries the database based on which role the
#user has selected
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

#Processing page for a successful login
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

#Confirmation page for a successful login
@app.route('/loggedout', methods=['GET'])
def loggedout():
	error = None
	return render_template('loggedout.html', error=error)

#Processing page for logging out. Deconstructs the global variables then pops the
#session information
@app.route('/logout')
def logout():
    t.deconstruct()
    s.deconstruct()
    p.deconstruct()
    session.pop('userid', None)
    session.pop('logged_in', None)
    return redirect(url_for('loggedout'))

#Lists all of the unique assignments for a course
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

#Processing page for assignment creation
@app.route('/Add', methods=['GET', 'POST'])
def assignmentAdd():
    courseNum = request.form['courseNum']
    t.submitAssignment(int(request.form['courseNum']),request.form['Title'], request.form['Description'], request.form['DueDate'])
    return redirect(url_for('assignmentCourse', courseNum = courseNum))

#Lists all of the submissions for a given assignment by pulling all students enrolled
#in the class then finding the assignments associated with them
@app.route('/Courses/<courseNum>/<assignTitle>/<sort>/<order>')
def List(courseNum, assignTitle, sort, order):
    listID =[]
    nameList = []
    gradeList = []
    assignID = []
    x=0
    if sort == "ID":
        temp = Query("SELECT * FROM students WHERE Course1 =" + str(courseNum) +" OR Course2 =" + str(courseNum) +" OR Course3 =" + str(courseNum) +" OR Course4 =" + str(courseNum) +" OR Course5 =" + str(courseNum) +" OR Course6 = " + str(courseNum) + " ORDER BY studentid " + order)
        for t in temp:
            listID.append(t[0])
            nameList.append(t[2] + " " + t[1])
            temp2 = Query("SELECT assignmentID, Grade FROM assignments WHERE StudentID =" + str(t[0]) + " AND Title = \"" + assignTitle + "\"")
            assignID.append(temp2[0][0])
            gradeList.append(temp2[0][1])
            x+=1
    elif sort == "Name":
        temp = Query("SELECT * FROM students WHERE Course1 =" + str(courseNum) +" OR Course2 =" + str(courseNum) +" OR Course3 =" + str(courseNum) +" OR Course4 =" + str(courseNum) +" OR Course5 =" + str(courseNum) +" OR Course6 = " + str(courseNum) + " ORDER BY Lname " + order)
        for t in temp:
            listID.append(t[0])
            nameList.append(t[2] + " " + t[1])
            temp2 = Query("SELECT assignmentID, Grade FROM assignments WHERE StudentID =" + str(t[0]) + " AND Title = \"" + assignTitle + "\"")
            assignID.append(temp2[0][0])
            gradeList.append(temp2[0][1])
            x+=1
    elif sort == "Submission":
        temp = Query("SELECT studentid, assignmentID, Grade FROM assignments WHERE Title = \"" + assignTitle + "\" AND courseid = " + courseNum + " ORDER BY Grade " + order)
        for t in temp:
            print(t)
            listID.append(t[0])
            assignID.append(t[1])
            gradeList.append(t[2])
            temp2 = Query("SELECT Fname, Lname FROM students WHERE StudentID =" + str(t[0]) )
            nameList.append(temp2[0][0] +" " + temp2[0][1])
            x+=1

    return render_template('StudentAssignments.html', studentIDs = listID, nameList = nameList, gradeList = gradeList, assignID = assignID, total = x, courseNum = courseNum, assignTitle = assignTitle)


#Shows a page that is prepopulated with the information about a particular assignment
#and allows the user to edit the values as desired
@app.route('/Courses/<courseNum>/<assignTitle>/Modify')
def Modify(courseNum, assignTitle):
    temp = Query("Select * FROM assignments WHERE Title =\"" + assignTitle + "\" AND courseID=" + str(courseNum))
    assignment = BPS.Assignment()
    assignment.init((int)(temp[0][0]), temp[0][1], temp[0][2], temp[0][3], temp[0][4], temp[0][5], temp[0][6])
    return render_template('ModifyAssignment.html', assignment = assignment, courseNum = courseNum)

#Processing page after a successful modification of an assignment
@app.route('/updating', methods=['GET', 'POST'])
def assignmentUpdate():
    courseNum = request.form['courseNum']
    title = request.form['origTitle']
    l = Query("UPDATE assignments SET title = \"" + request.form['Title'] + "\", dueDate = \"" + request.form['DueDate'] + "\", description = \"" + request.form['Description'] + "\" WHERE title = \""+ title + "\" AND CourseID =" + courseNum )
    return redirect(url_for('assignmentCourse', courseNum = courseNum))

#Processing page for the deletion of an assignment
@app.route('/Courses/<courseNum>/<assignTitle>/Delete')
def Delete(courseNum, assignTitle):
    temp = Query("DELETE FROM assignments WHERE CourseID=" + courseNum + " AND Title=\"" + assignTitle + "\"")

    return redirect(url_for('assignmentCourse', courseNum = courseNum))

#Brings up a small form for the teacher to give the student a grade
@app.route('/UpdateGrade/<assignmentID>')
def updateGradeHTML(assignmentID):
    return render_template("Grading.html", assignmentID=assignmentID)

#Processing page for a successful grade update
#redirects to the list of all submissions for an assignment
@app.route('/UpdatingGrade', methods=['GET', 'POST'])
def updateGrade():
    assignmentID = request.form['assignmentID']
    a = BPS.Assignment()
    a.initByID(assignmentID)
    a.updateGrade(request.form['Grade'])
    return redirect(url_for('List', courseNum =a.courseID, assignTitle=a.title, sort="ID", order="ASC"))

#Processing page for a successful message submission
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

#The teacher's view for all conversations that they currently have going on
@app.route("/Messages/<teacherID>")
def messagingTeacher(teacherID):
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

#The student's view for all ocnversations that they currently have going on
@app.route("/Messages/<studentID>")
def messagingStudent(studentID):
    q = "SELECT teacherID FROM messages WHERE studentID = " + studentID
    m = Query(q)
    a = []
    for ID in m:
        for teach in a:
            if stud.studentID != ID:
                teacher = BPS.Teacher()
                teacher.init(ID)
                a.append(teacher)
                break
    return render_template("MessageList.html", teachers=a, student = t)

#Shows all messages that were sent in a conversation as seen by a student.
@app.route("/Messages/<studentID>/<teacherID>")
def messagingStudentView(studentID, teacherID):
    q = "SELECT messageID FROM messages WHERE studentID = " + studentID + " AND teacherID = " + teacherID
    messages = Query(q)
    a = []
    for message in messages:
        m = BPS.Message()
        m.init(message)
        a.append(m)
    return render_template("MessageList.html", messages=a, student = s)

#shows all messages that were sent in a conversation as seen by a teacher.
@app.route("/Messages/<teacherID>/<studentID>")
def messagingTeacherView(teacherID, studentID):
    q = "SELECT messageID FROM messages WHERE studentID = " + studentID + " AND teacherID = " + teacherID
    messages = Query(q)
    a = []
    for message in messages:
        m = BPS.Message()
        m.init(message)
        a.append(m)
    return render_template("MessageList.html", teachers=a, student = t)

# declares and initialzes the global variables to be used throughout the program.
global t, s, p
t = BPS.Teacher()
s = BPS.Student()
p = BPS.Parent()
if __name__ == '__main__':
	app.run(host='127.0.0.1', port=8080, debug=True)
