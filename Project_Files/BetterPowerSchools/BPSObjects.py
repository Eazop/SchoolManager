import pymysql

class Assignment:
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
    def init(self, assignID, studID, Desc, CourID, Due, Gra):
        self.assignmentID = assignID

        self.studentID = studID
        self.description = Desc
        self.courseID = CourID
        self.dueDate = Due
        if(Gra != 'null'):
            self.grade = Gra

class Teacher:
    teacherID = 0
    currentCourses = []
    def init(self,teachID):
        self.teacherID = teachID
        db = pymysql.connect(host='104.196.175.51', user='BPS', password='betterpowerschools', db='better_power_schools')
        cur = db.cursor()
        q ="Select * from courses where TeacherID =" + str(self.teacherID)
        cur.execute(q)
        temp = cur.fetchall()
        for course in temp:
            self.currentCourses.append(course[0])
        db.close()

#Adds a new assignment to the data base
    def submitAssignment(self, courseID, Description, DueDate):
        studentHolder = []
        db = pymysql.connect(host='104.196.175.51', user='BPS', password='betterpowerschools', db='better_power_schools')
        cur = db.cursor()
        for x in range(1, 7):
            cur.execute('SELECT * FROM students WHERE Course' +str(x)+' = ' + str(courseID))
            l = cur.fetchall()
            for student in l:
                studentHolder.append(student[0])

        for student in studentHolder:
            q = 'INSERT INTO assignments (StudentID, Description, CourseID, DueDate) VALUES (' + str(student) + ', \"' + Description + '\", ' + str(courseID) + ', \"' + DueDate + '\")'
            cur.execute(q)
        db.commit()
        db.close()

#Returns a list of the assignment objects associated with the teacher
    def getAssignments(self):
        db = pymysql.connect(host='104.196.175.51', user='BPS', password='betterpowerschools', db='better_power_schools')
        cur = db.cursor()
        assignmentHolder = []
        for course in self.currentCourses:
            q = "SELECT * FROM assignments WHERE courseID = " + str(course)
            cur.execute(q)
            l = cur.fetchall()
            a = Assignment()
            a.init(l[0][0], l[0][1], l[0][2], l[0][3], l[0][4], l[0][5])
            assignmentHolder.append(a)
        return assignmentHolder
