import os
import sys
import shutil
import random
from cunyzero import db, bcrypt
from cunyzero.models import *


file = "./cunyzero/database.db"


if os.path.isfile(file):
    os.remove(file)                             # Deletes the old 'database.db' file if it exists.
else:
    print("Error: %s file not found" % file)

shutil.rmtree("./cunyzero/__pycache__")         # Deletes '__pycache__' directory and all its contents.


db.create_all()                                 # Create the new 'database.db' file from 'models.py'

# programs creation
program1 = Program(id=1, name="Bacholor of Computer Science")
program2 = Program(id=2, name="Bacholor of Computer Engineering")
db.session.add(program1)
db.session.add(program2)

# testing users
admin = Admin(ownerId=random.randint(10000000, 20000000))
student1 = Student(ownerId=random.randint(20000001, 30000000), programId=1, firstname="student", lastname="1")
student2 = Student(ownerId=random.randint(30000001, 40000000), programId=1, firstname="student", lastname="2")
student3 = Student(ownerId=random.randint(40000001, 50000000), programId=2, firstname="student", lastname="3")
student4 = Student(ownerId=random.randint(50000001, 60000000), programId=2, firstname="student", lastname="4")
student5 = Student(ownerId=random.randint(60000001, 70000000), programId=2, firstname="student", lastname="5")
student6 = Student(ownerId=random.randint(80000001, 90000000), programId=1, firstname="student", lastname="6")
student7 = Student(ownerId=random.randint(90000001, 100000000), programId=1, firstname="student", lastname="7")
student8 = Student(ownerId=random.randint(100000001, 110000000), programId=2, firstname="student", lastname="8")
student9 = Student(ownerId=random.randint(110000001, 120000000), programId=2, firstname="student", lastname="9")
student10 = Student(ownerId=random.randint(120000001, 130000000), programId=2, firstname="student", lastname="10")
 
instructor1 = Instructor(ownerId=random.randint(30000001, 40000000),  firstname="instructor", lastname="1")
instructor2 = Instructor(ownerId=random.randint(40000001, 50000000),  firstname="instructor", lastname="2")
instructor3 = Instructor(ownerId=random.randint(50000001, 60000000),  firstname="instructor", lastname="3")
instructor4 = Instructor(ownerId=random.randint(60000001, 70000000),  firstname="instructor", lastname="4")
instructor5 = Instructor(ownerId=random.randint(70000001, 80000000),  firstname="instructor", lastname="5")
instructor6 = Instructor(ownerId=random.randint(80000001, 90000000),  firstname="instructor", lastname="6")

user1 = User(username='admin', password=bcrypt.generate_password_hash('admin').decode('utf-8'), role='Admin')
student_user1 = User(username='student1', password=bcrypt.generate_password_hash('student').decode('utf-8'), role='Student')
student_user2 = User(username='student2', password=bcrypt.generate_password_hash('student').decode('utf-8'), role='Student')
student_user3 = User(username='student3', password=bcrypt.generate_password_hash('student').decode('utf-8'), role='Student')
student_user4 = User(username='student4', password=bcrypt.generate_password_hash('student').decode('utf-8'), role='Student')
student_user5 = User(username='student5', password=bcrypt.generate_password_hash('student').decode('utf-8'), role='Student')
student_user6 = User(username='student6', password=bcrypt.generate_password_hash('student').decode('utf-8'), role='Student')
student_user7 = User(username='student7', password=bcrypt.generate_password_hash('student').decode('utf-8'), role='Student')
student_user8 = User(username='student8', password=bcrypt.generate_password_hash('student').decode('utf-8'), role='Student')
student_user9 = User(username='student9', password=bcrypt.generate_password_hash('student').decode('utf-8'), role='Student')
student_user10 = User(username='student10', password=bcrypt.generate_password_hash('student').decode('utf-8'), role='Student')

instructor_user1 = User(username='instructor1', password=bcrypt.generate_password_hash('instructor').decode('utf-8'),
                        role='Instructor')
instructor_user2 = User(username='instructor2', password=bcrypt.generate_password_hash('instructor').decode('utf-8'),
                        role='Instructor')
instructor_user3 = User(username='instructor3', password=bcrypt.generate_password_hash('instructor').decode('utf-8'),
                        role='Instructor')
instructor_user4 = User(username='instructor4', password=bcrypt.generate_password_hash('instructor').decode('utf-8'),
                        role='Instructor')
instructor_user5 = User(username='instructor5', password=bcrypt.generate_password_hash('instructor').decode('utf-8'),
                        role='Instructor')
instructor_user6 = User(username='instructor6', password=bcrypt.generate_password_hash('instructor').decode('utf-8'),
                        role='Instructor')

user1.ownerId = admin.ownerId
student_user1.ownerId = student1.ownerId
student_user2.ownerId = student2.ownerId
student_user3.ownerId = student3.ownerId
student_user4.ownerId = student4.ownerId
student_user5.ownerId = student5.ownerId
student_user6.ownerId = student6.ownerId
student_user7.ownerId = student7.ownerId
student_user8.ownerId = student8.ownerId
student_user9.ownerId = student9.ownerId
student_user10.ownerId = student10.ownerId
instructor_user1.ownerId = instructor1.ownerId
instructor_user2.ownerId = instructor2.ownerId
instructor_user3.ownerId = instructor3.ownerId
instructor_user4.ownerId = instructor4.ownerId
instructor_user5.ownerId = instructor5.ownerId
instructor_user6.ownerId = instructor6.ownerId

# add students
db.session.add(student1)
db.session.add(student2)
db.session.add(student3)
db.session.add(student4)
db.session.add(student5)
db.session.add(student6)
db.session.add(student7)
db.session.add(student8)
db.session.add(student9)
db.session.add(student10)

# add instructors
db.session.add(instructor1)
db.session.add(instructor2)
db.session.add(instructor3)
db.session.add(instructor4)
db.session.add(instructor5)
db.session.add(instructor6)

# add admin
db.session.add(admin)

# add users
db.session.add(user1)
db.session.add(student_user1)
db.session.add(student_user2)
db.session.add(student_user3)
db.session.add(student_user4)
db.session.add(student_user5)
db.session.add(student_user6)
db.session.add(student_user7)
db.session.add(student_user8)
db.session.add(student_user9)
db.session.add(student_user10)
db.session.add(instructor_user1)
db.session.add(instructor_user2)
db.session.add(instructor_user3)
db.session.add(instructor_user4)
db.session.add(instructor_user5)
db.session.add(instructor_user6)

# add courses
course1 = Course(id=random.randint(10000000, 20000000), instructorId=instructor_user1.ownerId, dayofweek="MoTuWe", coursename="CSC103",
                startPeriod="1", endPeriod="9", capacity=5, creationPeriod=0)
course2 = Course(id=random.randint(20000001, 30000000), instructorId=instructor_user1.ownerId, dayofweek="Sa", coursename="CSC200",
                startPeriod="3", endPeriod="4", capacity=5, creationPeriod=0)
course3 = Course(id=random.randint(30000001, 40000000), instructorId=instructor_user2.ownerId, dayofweek="Su", coursename="CSC104",
                startPeriod="3", endPeriod="4", capacity=5, creationPeriod=0)
course4 = Course(id=random.randint(40000001, 50000000), instructorId=instructor_user2.ownerId, dayofweek="TuFr", coursename="CSC447",
                startPeriod="6", endPeriod="7", capacity=5, creationPeriod=0)
course5 = Course(id=random.randint(50000001, 60000000), instructorId=instructor_user3.ownerId, dayofweek="MoTu", coursename="CSC50",
                startPeriod="8", endPeriod="9", capacity=5, creationPeriod=0)
course6 = Course(id=random.randint(60000001, 70000000), instructorId=instructor_user4.ownerId, dayofweek="SaSu", coursename="CSC212",
                startPeriod="1", endPeriod="2", capacity=5, creationPeriod=0)
course7 = Course(id=random.randint(70000001, 80000000), instructorId=instructor_user5.ownerId, dayofweek="TuTh", coursename="CSC335",
                startPeriod="3", endPeriod="5", capacity=5, creationPeriod=0)
course8 = Course(id=random.randint(80000001, 90000000), instructorId=instructor_user6.ownerId, dayofweek="Fr", coursename="CSC322",
                startPeriod="4", endPeriod="4", capacity=5, creationPeriod=0)
db.session.add(course1)
db.session.add(course2)
db.session.add(course3)
db.session.add(course4)
db.session.add(course5)
db.session.add(course6)
db.session.add(course7)
db.session.add(course8)

# add course to student 2
student_2_Course2 = StudentCourse(courseId = course2.id, studentId = student_user2.ownerId, waiting = False)
student_2_Course3 = StudentCourse(courseId = course3.id, studentId = student_user2.ownerId, waiting = False)
student_2_Course4 = StudentCourse(courseId = course4.id, studentId = student_user2.ownerId, waiting = False)
student_2_Course5 = StudentCourse(courseId = course5.id, studentId = student_user2.ownerId, waiting = False)

db.session.add(student_2_Course2)
db.session.add(student_2_Course3)
db.session.add(student_2_Course4)
db.session.add(student_2_Course5)

def generateStudentCourse(studentId):
    db.session.add(StudentCourse(courseId = course2.id, studentId = studentId, waiting = False))
    db.session.add(StudentCourse(courseId = course3.id, studentId = studentId, waiting = False))
    db.session.add(StudentCourse(courseId = course4.id, studentId = studentId, waiting = False))
    db.session.add(StudentCourse(courseId = course5.id, studentId = studentId, waiting = False))

# course to student 3-6
generateStudentCourse(student_user3.ownerId)
generateStudentCourse(student_user4.ownerId)
generateStudentCourse(student_user5.ownerId)
generateStudentCourse(student_user6.ownerId)

#add period
period = Period(period=0)#course grading period
db.session.add(period)

#add review to student_2's course
student_2_Course2.review="Too much homework!"
student_2_Course2.rating=2
student_2_Course3.review="5 Hr exam"
student_2_Course3.rating=3
student_2_Course4.review="Good prof"
student_2_Course4.rating=4
student_2_Course5.review="Easy class"
student_2_Course5.rating=5

db.session.commit()

# course2.rating = course2.getAvgRating()
# course3.rating = course3.getAvgRating()
# course4.rating = course4.getAvgRating()
# course5.rating = course5.getAvgRating()
#
# db.session.commit()
# #testing warnings/period
# period.advanceNPeriod(50)# advances period 50 times and perform the task logic, warnings will be given accordingly

# warnings = Warning.query.all()
# if len(warnings)>=10:
#     for i in range(10):
#         warnings[i].justification="some justification"
# db.session.commit()

# complaint1 = Complaint(complainerId=user2.ownerId, targetId=user3.ownerId, message="Too bad")
# complaint2 = Complaint(complainerId=user3.ownerId, targetId=user2.ownerId, message="Deregister test")
# db.session.add(complaint1)
# db.session.add(complaint2)
# db.session.commit()