import pymysql

#The student class holds all the values for a student
#This should only be initialized if the user is logging in as a student successfully

class Student:
    firstName = None
    lastName = None
    studentID = None
    parentID = None
    courses = []

    #Initializes the class using just a studentID to pull the rest of the data from the database
    def init(self, studentID):
        q = Query("SELECT * FROM students WHERE studentID = " + str(studentID))
        self.studentID = q[0][0]
        self.firstName = q[0][1]
        self.lastName = q[0][2]
        self.parentID = q[0][3]
        for x in range(4, 10):
            if q[0][x] :
                c = Course()
                c.init(q[0][x])
                self.courses.append(c)

    def getParent(self):
        return parentID

    #Posts a new message in the database
    def sendMessage(self, message, teacherID):
        now = datetime.datetime.now()
        q = "INSERT INTO messages (StudentID, TeacherID, Message, Time) VALUES ("
        q += str(self.studentID) + ", " + str(teacherID) + ", " + message + ", " + now.strftime("%Y-%m-%d %H:%M") + ")"
        m = Query(q)

    #Sets all values back to their default (this should be used for logging out)
    def deconstruct(self):
        self.firstName = None
        self.lastName = None
        self.studentID = None
        self.parentID = None
        self.courses = []

class Parent:


    studentID = None
    parentID = None
    courses = []

    teacherID = 0
    currentCourses = []
    def init(self,parentID):
        self.parentID = parentID

    def getStudent(self):
        return studentID

    #Sets all values back to their default (this should be used for logging out)
    def deconstruct(self):
        self.firstName = None
        self.lastName = None
        self.studentID = None
        self.parentID = None
        self.courses = []
class Course:
    courseID = ""
    teacherID = ""
    subject = ""
    days = ""
    time = ""

    #Initializes the course using a set of given values
    def init(self, courseID, teacherID, subject, days, time):
        self.courseID = courseID
        self.teacherID = teacherID
        self.subject = subject
        self.days = days
        self.time = time

    #initialzes the course using just a course ID to pull the rest of the information from the database
    def init(self, courseID):
        q = Query("SELECT * from courses where courseID = " + str(courseID))
        print(q)
        self.courseID = courseID
        self.teacherID = q[0][1]
        self.subject = q[0][2]
        self.days = q[0][3]
        self.time = q[0][4]

    #Returns a list of assignments associated with the particular course
    def getAssignments(self):
        return Query("SELECT DISTINCT Description, DueDate FROM assignments WHERE CourseID =" + str(self.courseID()))

    #Sets all values of the course back to their default VALUES
    #This should be used whenever the user is done with it
    def deconstruct(self):
        self.courseID = None
        self.teacherID = None
        self.subject = None
        self.days = None
        self.time = None


class Assignment:
    title = None
    dueDate = None
    courseID = None
    studentID = None
    assignmentID = None
    description = None
    grade = None

#This initializes the assignment using just an assignmentID by pulling the rest
# of the values from the database.
    def initByID(self, assignID):
        self.assignmentID = assignID
        db = pymysql.connect(host='104.196.175.51', user='BPS', password='betterpowerschools', db='better_power_schools')
        cur = db.cursor()
        q = "SELECT * FROM assignments WHERE assignmentID = " + str(self.assignmentID)
        cur.execute(q)
        l = cur.fetchall()
        self.studentID = l[0][1]
        self.description =l[0][2]
        self.courseID = l[0][3]
        self.dueDate = l[0][4]
        if(l[0][5] != 'null'):
            self.grade = l[0][5]
        self.title = l[0][6]
        db.close()

#This initializes the assignment using given variables. This should only be used
# when the assignment is being created and added to the database
    def init(self, assignID, studID, Desc, CourID, Due, Gra, Title):
        self.assignmentID = assignID

        self.studentID = studID
        self.description = Desc
        self.courseID = CourID
        self.dueDate = Due
        if(Gra != 'null'):
            self.grade = Gra
        self.title = Title

    def deconstruct(self):
        self.title = None
        self.assignmentID = None
        self.studentID = None
        self.description = None
        self.dueDate = None
        self.grade = None

    def updateGrade(self,grade):
    
        l = Query("UPDATE assignments SET Grade=" + str(grade) + " WHERE assignmentID=" + str(self.assignmentID))
        self.grade = grade
#The teacher class holds all of the values of a teacher. It should match up
# exactly with the values that are in the database

class Teacher:
    teacherID = 0
    currentCourses = []
    def init(self,teachID):
        self.teacherID = teachID
        q ="Select CourseID from courses where TeacherID =" + str(self.teacherID)
        temp = Query(q)
        for course in temp:
            c = Course()
            c.init(course[0])
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
		db.close()
        return assignmentHolder

    def deconstruct(self):
        self.teacherID = None
        self.currentCourses = []


class Message:
    messageID = -1
    message = None
    studentID = None
    teacherID = None
    sendDate = None
 
	def initByAll(self, messageID, message, studentID, teacherID, sendDate):
		self.messageID = messageID
		self.message = message
		self.studentID = studentID
		self.teacherID = teacherID
		self.sendDate = sendDate
		
	def initByID(self, messageID):
		self.messageID = messageID
		q = "SELECT * FROM messages WHERE messageID = " + str(messageID)
		c = Query(q)
		self.message = c[1]
		self.studentID = c[2]
		self.teacherID = c[3]
		self.sendDate = c[4]
		
    def sendMessage(self):
         Query("INSERT INTO messages (StudentID, TeacherID, Message, Time) VALUES ("+ self.studentID + ", " + self.teacherID + ", " + self.message + ", " + self.sendDate +")" )

    def deconstruct(self):
        self.messageID = -1
        self.message = None
        self.studentID = None
        self.teacherID = None
        self.sendDate = None


def Query(query):
    db = pymysql.connect(host='104.196.175.51', user='BPS', password='betterpowerschools', db='better_power_schools')
    cur = db.cursor()
    cur.execute(query)
    db.commit()
    l = cur.fetchall()
    db.close()
    return l
