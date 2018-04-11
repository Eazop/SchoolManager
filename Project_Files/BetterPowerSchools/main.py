from flask import Flask, request, session, g, redirect, url_for, abort, \
 render_template, flash


from jinja2 import Template
import pymysql

class Course:
    courseID = ""
    teacherID = ""
    subject = ""
    days = ""
    time = ""

    def init(self, courseID, teacherID, subject, days, time):
        self.courseID = courseID
        self.teacherID = teacherID
        self.subject = subject
        self.days = days
        self.time = time

    def getAssignments(self):
        return Query("SELECT DISTINCT Description, DueDate FROM assignments WHERE CourseID =" + str(self.courseID()))



class Assignment:
    title = None
    dueDate = None
    courseID = None
    studentID = None
    assignmentID = None
    description = None
    grade = None

    def init(self, assignID):
        self.assignmentID = assignID
        db = pymysql.connect(host='104.196.175.51', user='BPS', password='betterpowerschools', db='better_power_schools')
        cur = db.cursor()
        q = "SELECT * FROM assignments WHERE assignmentID = " + str(self.assignmentID)
        cur.execute(q)
        l = cur.fetchall()
        self.studentID = l[1]
        self.description =l[2]
        self.courseID = l[3]
        self.dueDate = l[4]
        if(l[5] != 'null'):
            self.grade = l[5]
        self.title = l[6]
    def init(self, assignID, studID, Desc, CourID, Due, Gra, Title):
        self.assignmentID = assignID

        self.studentID = studID
        self.description = Desc
        self.courseID = CourID
        self.dueDate = Due
        if(Gra != 'null'):
            self.grade = Gra
        self.title = Title

class Teacher:
    teacherID = 0
    currentCourses = []
    def init(self,teachID):
        self.teacherID = teachID
        q ="Select * from courses where TeacherID =" + str(self.teacherID)
        temp = Query(q)
        for course in temp:
            c = Course()
            c.init(course[0], course[1], course[2], course[3], course[4])
            self.currentCourses.append(c)

#Adds a new assignment to the data base
    def submitAssignment(self, courseID, title, Description, DueDate):
        studentHolder = []
        db = pymysql.connect(host='104.196.175.51', user='BPS', password='betterpowerschools', db='better_power_schools')
        cur = db.cursor()
        for x in range(1, 7):
            cur.execute('SELECT * FROM students WHERE Course' +str(x)+' = ' + str(courseID))
            l = cur.fetchall()
            for student in l:
                studentHolder.append(student[0])

        for student in studentHolder:
            q = 'INSERT INTO assignments (StudentID, Description, CourseID, DueDate, Title) VALUES (' + str(student) + ', \"' + Description + '\", ' + str(courseID) + ', \"' + DueDate + '\", \"' + title + '\")'
            cur.execute(q)
        db.commit()
        db.close()

#Returns a list of the assignment objects associated with the teacher
    def getAssignments(self):
        db = pymysql.connect(host='104.196.175.51', user='BPS', password='betterpowerschools', db='better_power_schools')
        cur = db.cursor()
        assignmentHolder = []
        for course in self.currentCourses:
            q = "SELECT * FROM assignments WHERE CourseID = " + str(course.courseID)
            cur.execute(q)
            l = cur.fetchall()
            for assignment in l:
                a = Assignment()
                a.init(assignment[0], assignment[1], assignment[2], assignment[3], assignment[4], assignment[5])
                assignmentHolder.append(a)
        return assignmentHolder

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
        courses = t.currentCourses
        return render_template('home.html', courses = courses)


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
                temp = Assignment()
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

global t
t = Teacher()

if __name__ == '__main__':
	app.run(host='127.0.0.1', port=8080, debug=True)
