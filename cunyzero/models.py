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

class Admin(db.Model): #Admin.user, User.adminOwner
    ownerId = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    user = db.relationship('User', backref='adminOwner', lazy=True)
    #taboo_list = db.Column(db.Text, nullable = False, default='')#f**k, etc.

    def __repr__(self):
        return f"Admin('{self.ownerId}')"

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
    status = db.Column(db.String(20), default=None)#suspended, graduated, etc.
    fine = db.Column(db.Float, nullable = False, default=0)
    gpa = db.Column(db.Float, nullable = False, default=0.0)

    user = db.relationship('User', backref='studentOwner', lazy=True)
    courses = db.relationship('StudentCourse', backref='student', lazy=True)
    application = db.relationship('GraduationApplication', backref='applicant', lazy=True)
    warnings = db.relationship('Warning', backref='targetStudent', lazy=True)
    #wait_list = db.relationship('StudentCourse', backref='student', lazy=True)
    #complaints = db.relationship('Complaint', backref='target', lazy=True)

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
            course = Course.query.filter_by(id=sc.courseId, status="Open").first()
            if course.id in filterIds:#if its waitlisted/enrolled
                courses.append(course)
        return courses
    def notEnrolled(self):#return courses that student is not enrolled or waitlisted in
        studentCoursesIds = [sc.courseId for sc in StudentCourse.query.filter_by(studentId=self.ownerId)]
        return [course for course in Course.query.all() if course.id not in studentCoursesIds]

class Instructor(db.Model):
    ownerId = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), default=None)#fired, suspended, etc.
    firstname = db.Column(db.String(30), nullable=False)
    lastname = db.Column(db.String(30), nullable=False)

    user = db.relationship('User', backref='instructorOwner', lazy=True)
    warnings = db.relationship('Warning', backref='targetInstructor', lazy=True)
    complaints = db.relationship('Complaint', backref='target', lazy=True)
    def __repr__(self):
        return '<instructorid: %r>' % self.ownerId


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
    waitlist_capacity = db.Column(db.Integer, default=30)
    #gpa = db.Column(db.Float, nullable = True) # can be calculated with StudentCourse
    #rating = db.Column(db.Float, nullable = True)# ^

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
        return StudentCourse.query.filter_by(courseId=self.id).count()

class StudentCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    courseId = db.Column(db.Integer, db.ForeignKey('course.id'),nullable=False)
    studentId = db.Column(db.Integer,db.ForeignKey('student.ownerId'),nullable = False)

    gpa = db.Column(db.Float,nullable = True)
    rating = db.Column(db.Integer, nullable = True)
    review = db.Column(db.Text, nullable = True)
    waiting = db.Column(db.Boolean,nullable = False, default=False)

    def __repr__(self):
        return '<courseid: %r, studentid: %r>' % (self.courseId, self.studentId)


class Period(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    period_num = db.Column(db.Integer, nullable = False)#periods passed
    period = db.Column(db.String(20), nullable = False)#current period
    
    def __repr__(self):
        return '<period: %r>' % self.period


class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    complainerId = db.Column(db.Integer,db.ForeignKey('student.ownerId'), nullable=False)
    targetId = db.Column(db.Integer, db.ForeignKey('student.ownerId'), db.ForeignKey('instructor.ownerId'))
    message = db.Column(db.Text, nullable=False, default='')
    processed = db.Column(db.Boolean, nullable=False, default=False) #check the complaint is processed by admin or not

    def __repr__(self):
        return '<complainer: %r, complainee: %r>' % (self.complainerId, self.targetId)


class Warning(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('student.ownerId'), db.ForeignKey('instructor.ownerId'), nullable=False)
    message = db.Column(db.Text, nullable=False, default='')
    def __repr__(self):
        return '<Warning: %r>' % self.id


class GraduationApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    studentId = db.Column(db.Integer,db.ForeignKey('student.ownerId'),unique = True, nullable = False)

    # For registrar Use
    justification = db.Column(db.Text, nullable=False, default='')
    approval = db.Column(db.Boolean,  default=None)   # None: waiting for registrar to make decision

    def __repr__(self):
        return '<GradApplication: >' % self.id

class Waitlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    courseId = db.Column(db.Integer,db.ForeignKey('course.id'), nullable=False)
    studentId = db.Column(db.Integer,db.ForeignKey('student.ownerId'),nullable = False)
    def __repr__(self):
        return '<courseid: %r, studentid: %r>' % (self.courseId, self.studentId)

