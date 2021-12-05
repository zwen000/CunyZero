from flask.helpers import flash
from wtforms.fields.core import DecimalField
from cunyzero import db, login_manager
from datetime import datetime
from flask_login import UserMixin

# is_authenticated, return true if valid credentials are provided
# is_active,
# is_anonymous
# get_id

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
 


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    role = db.Column(db.String(30), nullable=False, default='Visitor')
    ownerId = db.Column(db.Integer, db.ForeignKey('visitor.ownerId'), db.ForeignKey('admin.ownerId'), db.ForeignKey('student.ownerId'), db.ForeignKey('instructor.ownerId'))

    def __repr__(self):
        return f"User('{self.username}, {self.id}, {self.role}, {self.ownerId}')"
    def userid(self):
        return self.id
    def getPeriodName(self):
        return Period.query.all()[0].getPeriodName()

class Admin(db.Model): #Admin.user, User.adminOwner
    ownerId = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    user = db.relationship('User', backref='adminOwner', lazy=True)
    taboo_list = db.Column(db.Text, nullable = False, default='')#f**k, etc.

    def __repr__(self):
        return f"Admin('{self.ownerId}')"
    def getTabooList(self):
        return self.taboo_list.split(" ")

class Visitor(db.Model): 
    ownerId = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    user = db.relationship('User', backref='visitorOwner', lazy=True)
    applications = db.relationship('Application', backref='applicant', lazy=True)

    def __repr__(self):
        return f"Visitor('{self.ownerId}')"

class Student(db.Model):
    ownerId = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(30), nullable=False)
    lastname = db.Column(db.String(30), nullable=False)
    programId = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    honor = db.Column(db.Integer, nullable = False, default=0)
    status = db.Column(db.String(20), default='Employed')#suspended, graduated, etc.
    fine = db.Column(db.Float, nullable = False, default=0)
    gpa = db.Column(db.Float, nullable = False, default=0.0)
    warning = db.Column(db.Integer, nullable = False, default=0)
    enrollmentPermission = db.Column(db.Boolean, nullable=False, default=False)#special enrollment permission

    user = db.relationship('User', backref='studentOwner', lazy=True)
    courses = db.relationship('StudentCourse', backref='student', lazy=True)
    application = db.relationship('GraduationApplication', backref='applicant', lazy=True)
    warnings = db.relationship('Warning', backref='targetStudent', lazy=True)
    complaints = db.relationship('Complaint', backref='targetStudent', primaryjoin="Student.ownerId==Complaint.targetId", lazy=True)# complaints targeting/complaining about this student
    myComplaints = db.relationship('Complaint', backref='complainingStudent', primaryjoin="Student.ownerId==Complaint.complainerId", lazy=True)# complaints from this student about others

    def __repr__(self):
        return '<studentid: %r>' % self.ownerId
    def getWaitList(self):#return studentcourse that student is waiting for
        return StudentCourse.query.filter_by(studentId=self.ownerId, waiting=True)
    def enrolled(self):
        return self.getWaitingCourses(False)
    def waitListed(self):
        return self.getWaitingCourses(True)
    def getWaitingCourses(self, waiting):#returns waitlisted courses if waiting=true else if waiting=false return enrolled courses
        studentCourses = StudentCourse.query.filter_by(studentId=self.ownerId, waiting=waiting)
        filterIds = [sc.courseId for sc in studentCourses]
        courses = []
        for sc in studentCourses:# for each studentcourse
            if sc.gpa != 'W':
                course = Course.query.filter_by(id=sc.courseId, status="Open").first()
                if course:
                    if course.id in filterIds:#if its waitlisted/enrolled
                        courses.append(course)
        return courses
    def notEnrolled(self):#return courses that student is not enrolled or waitlisted in
        studentCoursesIds = [sc.courseId for sc in StudentCourse.query.filter_by(studentId=self.ownerId)]
        return [course for course in Course.query.filter_by(status="Open") if course.id not in studentCoursesIds]
    def getCurrentCourses(self):
        studentCourses = StudentCourse.query.filter_by(studentId=self.ownerId)
        currentCourses = []
        for studentcourse in studentCourses:
            if studentcourse.course.status == "Open":
                currentCourses.append(studentcourse)
        return currentCourses
    def getSemesterGpa(self):#return prev semester gpa
        count = 0
        total = 0.0
        period = Period.query.all()[0]
        for sc in self.courses:
            if sc.gpa and sc.creationSemester()==period-1:
                count+=1
                total+=sc.getFloat()
        if count == 0:
            return 4.0
        else:
            return total/count
    def getOverallGpa(self):#return overall gpa
        count = 0
        total = 0.0
        for sc in self.courses:
            if sc.gpa:
                count+=1
                total+=sc.getFloat()
        if count == 0:
            return 0.0
        else:
            return total/count
    def terminate(self):#terminate student
        #delete courses
        StudentCourse.query.filter_by(studentId=self.ownerId).delete()
        #delete complaints
        Complaint.query.filter_by(complainerId=self.ownerId).delete()
        Complaint.query.filter_by(targetId=self.ownerId).delete()
        #delete warnings
        Warning.query.filter_by(userId=self.ownerId).delete()
        #delete graduation application
        GraduationApplication.query.filter_by(studentId=self.ownerId).delete()
        #delete user
        User.query.filter_by(ownerId=self.ownerId)
        #delete student
        Student.query.filter_by(ownerId=self.ownerId).delete()
        db.session.commit()

class Instructor(db.Model):
    ownerId = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), default='Employed')#fired, suspended, etc.
    firstname = db.Column(db.String(30), nullable=False)
    lastname = db.Column(db.String(30), nullable=False)
    warning = db.Column(db.Integer, nullable = False, default=0)

    user = db.relationship('User', backref='instructorOwner', lazy=True)
    warnings = db.relationship('Warning', backref='targetInstructor', lazy=True)
    complaints = db.relationship('Complaint', backref='targetInstructor', primaryjoin="Instructor.ownerId==Complaint.targetId", lazy=True)# complaints targeting/complaining about this instructor
    myComplaints = db.relationship('Complaint', backref='complainingInstructor', primaryjoin="Instructor.ownerId==Complaint.complainerId", lazy=True)# complaints from this instructor about other students
    courses = db.relationship('Course', backref='instructor', lazy=True)
    def __repr__(self):
        return '<instructorid: %r>' % self.ownerId
    # def terminate(self):#dont use since its weird what to do with existing courses instructor teaches
    #     #delete complaints
    #     Complaint.query.filter_by(complainerId=self.ownerId).delete()
    #     Complaint.query.filter_by(targetId=self.ownerId).delete()
    #     #delete warnings
    #     Warning.query.filter_by(userId=self.ownerId).delete()
    #     #delete user
    #     User.query.filter_by(ownerId=self.ownerId)
    #     #delete instructor
    #     Instructor.query.filter_by(ownerId=self.ownerId).delete()
    #     db.session.commit()


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(30), nullable=False)
    lastname = db.Column(db.String(30), nullable=False)
    intro = db.Column(db.Text, nullable=False) # self introduction
    type = db.Column(db.Enum("Instructor", "Student"), nullable=False)
    visitor_id = db.Column(db.Integer, db.ForeignKey('visitor.ownerId'), nullable=False)

    # for student only
    GPA = db.Column(db.Integer, unique=False, nullable=False, default=0) # only student applicant has a GPA
    program_name = db.Column(db.String(20), db.ForeignKey('program.name')) # only student need to apply to a program

    # For registrar Use
    justification = db.Column(db.Text, nullable=False, default='')
    approval = db.Column(db.Boolean,  default=None)   # None: waiting for registrar to make decision

    def __repr__(self):
        return f"Application({self.id}, {self.firstname}, {self.lastname}, {self.approval})"


class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False, default=10)
    enrolled_total = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"Program('{self.id}', '{self.name}', '{self.enrolled_total}', '{self.capacity}')"


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instructorId = db.Column(db.Integer, db.ForeignKey('instructor.ownerId'))
    coursename = db.Column(db.String(20), nullable = False, unique = True)

    creationPeriod = db.Column(db.Integer, nullable = True)#for period/semester task logic
    startPeriod = db.Column(db.Integer, nullable = False)#1-9
    endPeriod = db.Column(db.Integer, nullable = False)#1-9
    dayofweek = db.Column(db.String(30), nullable = False)#mo,tu,we,th,fr,sa,su if missing use -- 
    capacity = db.Column(db.Integer, default=30)
    status = db.Column(db.String(20), nullable = False, default="Open")#status like open, finished, cancelled, etc.
    
    #wait_list = db.relationship('Waitlist', backref='course', lazy=True)
    waitListCapacity = db.Column(db.Integer, default=30)
    #gpa = db.Column(db.Float, nullable = True) # can be calculated with StudentCourse
    rating = db.Column(db.Float, default=None, nullable = True)# ^
    studentcourses = db.relationship('StudentCourse', backref='course', lazy=True)

    def __repr__(self):
        return '<Course %r, %r>' % (self.coursename, self.status)
    def getInstructorName(self):
        instructor = Instructor.query.get(self.instructorId)
        return instructor.firstname + " " + instructor.lastname
    def getWaitList(self):#return waitlist (studentcourse with waiting=true)
        return StudentCourse.filter_by(courseId=self.id, waiting=True)
    #pre: must be a real studentId
    #post: return true if conflict with student's course(inluding waitlisted courses) else false                   
    def courseConflict(self, studentId):
        courses = StudentCourse.query.filter_by(studentId=studentId)
        days = []
        for i in range(int(len(self.dayofweek)/2)):#get list of days: [Mo, Tu, Etc.]
            days.append(self.dayofweek[i*2:i*2+2])
        for studentcourse in courses:#check all the student's courses
            course = Course.query.filter_by(id=studentcourse.courseId).first()
            enrolled_dayofweek = course.dayofweek
            for day in days:#go through each day in list of days
                if day in enrolled_dayofweek:#if day conflict
                    #check if period conflicts
                    if self.conflictPeriod(course.startPeriod, course.endPeriod, self.startPeriod, self.endPeriod):
                        return True
        return False
    def conflictPeriod(self, start, end, start2, end2):
        return self.conflictNum(start, end, start2, end2) or self.conflictNum(start2, end2, start, end)
    def conflictNum(self,start, end, start2, end2):
        if start>=start2 and start<=end2:
            return True
        if end>=start2 and end<=end2:
            return True
    def getEnrolledTotal(self):
        return StudentCourse.query.filter_by(courseId=self.id, waiting=False).count()
    def getWaitlistTotal(self):
        return StudentCourse.query.filter_by(courseId=self.id, waiting=True).count()
    def getClassGpa(self):
        count=0
        total=0.0
        for sc in self.studentcourses:
            if sc.gpa:
                count+=1
                total+=sc.getFloat()
        if count != 0:
            return total/count
        else:
            return None
    def getAvgRating(self):
        count=0
        total=0.0
        for sc in self.studentcourses:
            if sc.rating:
                count+=1
                total+=sc.rating
        if count != 0:
            return total/count
        else:
            return None
    def getStudentGrade(self, student_id):
        studentCourse = StudentCourse.query.filter_by(courseId=self.id, studentId=student_id).first()
        if studentCourse:
            return studentCourse.gpa
        else:
            return None

class StudentCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    courseId = db.Column(db.Integer, db.ForeignKey('course.id'),nullable=False)
    studentId = db.Column(db.Integer,db.ForeignKey('student.ownerId'),nullable = False)

    gpa = db.Column(db.Text,nullable = True)
    rating = db.Column(db.Integer, nullable = True)
    review = db.Column(db.Text, nullable = True)
    visible = db.Column(db.Boolean, nullable = False, default=True)#if too many taboo words hide review
    waiting = db.Column(db.Boolean,nullable = False, default=False)

    def __repr__(self):
        return '<courseid: %r, studentid: %r>' % (self.courseId, self.studentId)
    def creationSemester(self):
        return self.course.creationPeriod
    def getCourseName(self):
        return self.course.coursename

    # The function will return a float grade base the the grade scale
    def getFloat(self):
        grade_scale = {
            'A+': 4.0,
            'A': 4.0,
            'A-': 3.7,
            'B+': 3.3,
            'B': 3.0,
            'B-': 2.7,
            'C+': 2.3,
            'C': 2.0,
            'C-': 1.7,
            'D+': 1.3,
            'D': 1.0,
            'F': 0.0,
            'W': None,
        }
        return grade_scale[self.gpa]

    def getCourseName(self):
        course = Course.query.get(self.courseId)
        return course.coursename
    def checkTabooWords(self):#check if review has taboowords and removes them and flags review accordingly
        review= self.review
        tempReview = self.review
        tabooList = Admin.query.all()[0].getTabooList()
        count = 0
        for tabooWord in tabooList:
            temp = review
            while(tabooWord in temp):
                count+=1
                temp = temp[temp.find(tabooWord)+1:]
                tempReview=tempReview.replace(tabooWord, "*")
        #1-2 taboo words replace with *, +1 to warning
        if count==1 or count==2:
            self.review=tempReview
            self.student.warning+=1
            warning = Warning(userId=self.studentId, message="Review has 1-2 Taboo Words, Warning +1")
            db.session.add(warning)
            flash("1-2 Taboo Words! Warning +1", 'danger')
        #>=3 taboo words reviews invisible, +2 to warning
        elif count>=3:
            self.visible=False
            self.student.warning+=2
            warning = Warning(userId=self.studentId, message="Review has >=3 Taboo Words, Warning +2")
            db.session.add(warning)
            flash("3 of more Taboo Words! Review is now invisible, Warning+2!", 'danger')
        db.session.commit()

class Period(db.Model):#set-up, registration, running, or grading period
    id = db.Column(db.Integer, primary_key=True)
    period = db.Column(db.Integer, nullable = False, default=0)#periods passed
    #period = db.Column(db.String(20), nullable = False)#current period
    
    def __repr__(self): 
        return '<period: %r>' % self.period
    def getPeriodName(self):# returns set-up, registration, running, or grading period
        remainder = self.period % 4
        if remainder==0:
            return "Course Set-up Period"
        if remainder==1:
            return "Course Registration Period"
        if remainder==2:
            return "Course Running Period"
        if remainder==3:
            return "Grading Period"
    def advanceNPeriod(self, n):#calls advance period n times
        for i in range(n):
            self.advancePeriod()
    def advancePeriod(self):#advance to next period and perform task logic
        self.nextPeriodLogic()# do task logic when period changes
        self.period+=1# advance period by 1
        db.session.commit() # update db
    def nextPeriodLogic(self):# corresponding logic depending on the next period
        nextPeriod = (self.period+1)%4
        if nextPeriod == 0:# next is Course Set-up Period
            # Update the student overall gpa to Student
            for student in Student.query.filter_by(status='Employed'):
                student.gpa = student.getOverallGpa()
            db.session.commit()
            # unsuspend students and instructors 
            for student in Student.query.filter_by(status="Suspended"):
                student.status = "Employed"
            for instructor in Instructor.query.filter_by(status="Suspended"):
                instructor.status = "Employed"
            db.session.commit()
            # student whose semester gpa>3.75 or overall gpa>3.5 + 1 to honor
            #student whose gpa <2 or failed same course twice terminated
            for student in Student.query.all():
                overAllGpa = student.gpa
                if student.getSemesterGpa()>3.75 or overAllGpa>3.5:
                    student.honor+=1
                elif overAllGpa<2:
                    student.terminate()
            #instructor whose class gpa >3.5 or <2.5 warned/fired(didnt add fire yet) unless justified
            #instructor whose avgclass rating<2 receive 1 warning
            for course in Course.query.all():
                classGpa = course.getClassGpa()
                if classGpa<2.5 or classGpa>3.5:
                    course.instructor.warning+=1
                    warning = Warning(userId=instructor.ownerId, 
                                            message="Class Gpa >3.5 or <2.5, until further justification, warning +1",
                                            semesterWarned=self.period+1)
                    db.session.add(warning)
                if course.getAvgRating()<2:
                    course.instructor.warning+=1
                    warning = Warning(userId=instructor.ownerId, 
                                            message="Average class rating <2, warning +1",
                                            semesterWarned=self.period+1)
                    db.session.add(warning)
            #student failed same course twice terminated
            for student in Student.query.all():
                dict={}#key,value: coursename,gpa ('F', 'A', etc.)
                for sc in self.courses:
                    coursename = sc.getCourseName()
                    if coursename in dict:#if key in dict
                        if dict[coursename]=='F':
                            if sc.gpa=='F':
                                student.terminate()
                                break
                    else:
                        dict[coursename]=sc.gpa
            # student suspended and pay fine if warning>=3
            for student in Student.query.all():
                if student.warning>=3:
                    if student.honor>1:#if there is honor
                        if student.honor>student.warning:# if more honor than warning no suspension, remove warnings
                            student.honor-=student.warning
                            student.warning=0
                        else:#if honor<=warning remove warnings with honor
                            student.warning-=student.honor
                            student.honor=0
                            if student.warning>=3:#if still 3 warnings, suspend
                                student.status = "Suspended"
                                student.warning-=3
                                student.fine +=50.0
                    else:
                        student.status = "Suspended"
                        student.warning-=3
                        student.fine +=50.0
            # instructor didnt assign all grades receive 1 warning
            warnedInstructors = []
            for course in Course.query.filter_by(status="Open"):
                instructor = course.instructor
                if instructor not in warnedInstructors:
                    for studentcourse in course.studentcourses:
                        if not studentcourse.gpa:
                            warnedInstructors.append(instructor.ownerId)
                            instructor.warning+=1
                            warning = Warning(userId=instructor.ownerId, 
                                            message="Didn't assign every student a grade! warning +1",
                                            semesterWarned=self.period+1)
                            db.session.add(warning)
                            break
            # instructor whose courses are all canceled suspended
            for instructor in Instructor.query.filter_by(status="Employed"):
                canceled = False
                for course in instructor.courses:
                    if course.status=="Open":
                        break
                    if course.status=="Canceled":
                        canceled = True
                if canceled:# all courses canceled
                    instructor.status = "Suspended"
            # instructor 3 warning suspended
            for instructor in Instructor.query.filter_by(status="Employed"):
                if instructor.warning>=3:
                    instructor.status = "Suspended"
                    instructor.warning-=3
            # previous semester's courses are now finished
            for course in Course.query.filter_by(status="Open"):
                course.status = "Finished"
        elif nextPeriod == 1:# next is Course Registration Period
            pass
        elif nextPeriod == 2:# next is Course Running Period
            # course < 5 student canceled, students get extra chance to register
            for course in Course.query.filter_by(status="Open"):
                studentcourses = course.studentcourses
                if len(studentcourses)<5:
                    instructor = course.instructor
                    instructor.warning+=1
                    warning = Warning(userId=instructor.ownerId, 
                                        message=f"Course {course.coursename} has <5 students, course canceled! warning +1", 
                                        semesterWarned=self.period+1+1)
                    db.session.add(warning)
                    for studentcourse in studentcourses:
                        studentcourse.student.enrollmentPermission = True
            # warn student with < 2 courses if no special permission
            for student in Student.query.all():
                if not student.enrollmentPermission:
                    if len(student.getCurrentCourses())<2:
                        student.warning+=1
                        warning = Warning(userId=student.ownerId, 
                                    message="you are enrolled in <2 courses! warning +1",
                                    semesterWarned=self.period+1)
                        db.session.add(warning)
        elif nextPeriod==3:# next is Grading Period
            # warn student < 2 courses with special permission
            for student in Student.query.all():
                if student.enrollmentPermission:
                    if len(student.getCurrentCourses())<2:
                        student.warning+=1
                        warning = Warning(userId=student.ownerId, 
                                        message="you are enrolled in <2 courses! warning +1",
                                        semesterWarned = self.period+1)
                        db.session.add(warning)
                    student.enrollmentPermission = False # remove special permission
        db.session.commit()

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    complainerId = db.Column(db.Integer,db.ForeignKey('student.ownerId'), db.ForeignKey('instructor.ownerId'), nullable=False)
    targetId = db.Column(db.Integer, db.ForeignKey('student.ownerId'), db.ForeignKey('instructor.ownerId'))
    message = db.Column(db.Text, nullable=False, default='')
    processed = db.Column(db.Boolean, nullable=False, default=False) #check the complaint is processed by admin or not

    def __repr__(self):
        return '<complainer: %r, complainee: %r>' % (self.complainerId, self.targetId)


class Warning(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('student.ownerId'), db.ForeignKey('instructor.ownerId'), nullable=False)
    message = db.Column(db.Text, nullable=False, default='')

    semesterWarned = db.Column(db.Integer, nullable=False, default=0)# period/semester warning was sent
    justification = db.Column(db.Text, nullable=False, default='')# if null then admin dont need to process it
    result = db.Column(db.Text, nullable=False, default='') # if result=='' warning is not yet processed, else has the processed result
    def __repr__(self):
        return '<Warning: %r, message: %r>' % (self.id, self.message)
    def thisSemester(self, period):#returns true if semester warned is this semester
        return (self.semesterWarned/4)==(period/4)
    def prevSemester(self, period):#returns true if semester warned is prev semester
        return self.thisSemester(period-4)


class GraduationApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    studentId = db.Column(db.Integer,db.ForeignKey('student.ownerId'),unique = True, nullable = False)

    # For registrar Use
    justification = db.Column(db.Text, nullable=False, default='')
    approval = db.Column(db.Boolean,  default=None)   # None: waiting for registrar to make decision

    def __repr__(self):
        return '<GradApplication: >' % self.id


