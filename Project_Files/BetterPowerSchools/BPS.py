import pymysql

class Student:
    firstName = None
    lastName = None
    studentID = None
    parentID = None
    courses = []

    def init(self, studentID):
        q = Query("SELECT * FROM students WHERE studentID = " + str(studentID))
        self.studentID = q[0]
        self.firstName = q[1]
        self.lastName = q[2]
        self.parentID = q[3]
        for x in range(4, 10):
            if q[x] :
                c = Course()
                c.init(q[x])
                courses.append(c)

    def getParent(self):
        return parentID

    def sendMessage(self, message, teacherID):
        now = datetime.datetime.now()
        q = "INSERT INTO messages (StudentID, TeacherID, Message, Time) VALUES ("
        q += str(self.studentID) + ", " + str(teacherID) + ", " + message + ", " + now.strftime("%Y-%m-%d %H:%M") + ")"
        m = Query(q)


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

    def init(self, courseID):
        q = Query("SELECT * from courses where courseID = " + str(courseID))
        print(q)
        self.courseID = courseID
        self.teacherID = q[0][1]
        self.subject = q[0][2]
        self.days = q[0][3]
        self.time = q[0][4]

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

#This initializes the assignment using just an assignmentID by pulling the rest
# of the values from the database.
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
        return assignmentHolder

class Message:
    messageID
    message = None
    studentID = None
    teacherID = None
    sendDate = None

    # def sendMessage(self):
    #     Query("INSERT INTO messages (StudentID, TeacherID, Message, Time) VALUES ("+ self.studentID + ", ")


def Query(query):
    db = pymysql.connect(host='104.196.175.51', user='BPS', password='betterpowerschools', db='better_power_schools')
    cur = db.cursor()
    cur.execute(query)
    l = cur.fetchall()
    db.close()
    return l
