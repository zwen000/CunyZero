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
student2 = Student(ownerId=random.randint(20000001, 30000000), programId=1, firstname="student", lastname="2")
student3 = Student(ownerId=random.randint(20000001, 30000000), programId=2, firstname="student", lastname="3")
student4 = Student(ownerId=random.randint(20000001, 30000000), programId=2, firstname="student", lastname="4")
student5 = Student(ownerId=random.randint(20000001, 30000000), programId=2, firstname="student", lastname="5")

instructor1 = Instructor(ownerId=random.randint(30000001, 40000000),  firstname="instructor", lastname="1")
instructor2 = Instructor(ownerId=random.randint(30000001, 40000000),  firstname="instructor", lastname="2")

user1 = User(username='admin', password=bcrypt.generate_password_hash('admin').decode('utf-8'), role='Admin')
student_user1 = User(username='student1', password=bcrypt.generate_password_hash('student1').decode('utf-8'), role='Student')
student_user2 = User(username='student2', password=bcrypt.generate_password_hash('student2').decode('utf-8'), role='Student')
student_user3 = User(username='student3', password=bcrypt.generate_password_hash('student3').decode('utf-8'), role='Student')
student_user4 = User(username='student4', password=bcrypt.generate_password_hash('student4').decode('utf-8'), role='Student')
student_user5 = User(username='student5', password=bcrypt.generate_password_hash('student5').decode('utf-8'), role='Student')

instructor_user1 = User(username='instructor1', password=bcrypt.generate_password_hash('instructor1').decode('utf-8'),
                        role='Instructor')
instructor_user2 = User(username='instructor2', password=bcrypt.generate_password_hash('instructor2').decode('utf-8'),
                        role='Instructor')

user1.ownerId = admin.ownerId
student_user1.ownerId = student1.ownerId
student_user2.ownerId = student2.ownerId
student_user3.ownerId = student3.ownerId
student_user4.ownerId = student4.ownerId
student_user5.ownerId = student5.ownerId
instructor_user1.ownerId = instructor1.ownerId
instructor_user2.ownerId = instructor2.ownerId

# add students
db.session.add(student1)
db.session.add(student2)
db.session.add(student3)
db.session.add(student4)
db.session.add(student5)

# add instructors
db.session.add(instructor1)
db.session.add(instructor2)

# add admin
db.session.add(admin)

# add users
db.session.add(user1)
db.session.add(student_user1)
db.session.add(student_user2)
db.session.add(student_user3)
db.session.add(student_user4)
db.session.add(student_user5)
db.session.add(instructor_user1)
db.session.add(instructor_user2)

# #testing courses
course1 = Course(id=random.randint(10000000, 20000000), instructorId=instructor_user1.ownerId, dayofweek="MoTuWe", coursename="CSC1",
                startPeriod="1", endPeriod="9", capacity=5, creationPeriod=0)
course2 = Course(id=random.randint(20000001, 30000000), instructorId=instructor_user1.ownerId, dayofweek="Sa", coursename="CSC2",
                startPeriod="3", endPeriod="4", capacity=5, creationPeriod=0)
course3 = Course(id=random.randint(30000001, 40000000), instructorId=instructor_user2.ownerId, dayofweek="Su", coursename="CSC3",
                startPeriod="3", endPeriod="4", capacity=5, creationPeriod=0)
course4 = Course(id=random.randint(40000001, 50000000), instructorId=instructor_user2.ownerId, dayofweek="TuThFr", coursename="CSC4",
                startPeriod="3", endPeriod="4", capacity=5, creationPeriod=0)

db.session.add(course1)
db.session.add(course2)
db.session.add(course3)
db.session.add(course4)
# db.session.add(course5)

# studentCourse2 = StudentCourse(courseId = course2.id, studentId = user2.ownerId, waiting = True)
# studentCourse3 = StudentCourse(courseId = course3.id, studentId = user2.ownerId, waiting = True)
# studentCourse4 = StudentCourse(courseId = course4.id, studentId = user2.ownerId, waiting = False)
# studentCourse5 = StudentCourse(courseId = course5.id, studentId = user2.ownerId, waiting = False)
#
# db.session.add(studentCourse2)
# db.session.add(studentCourse3)
# db.session.add(studentCourse4)
# db.session.add(studentCourse5)

#testing period
period = Period(period=0)#course grading period
db.session.add(period)

#testing review
# studentCourse2.review="testing review"
# studentCourse2.rating=2
# studentCourse3.review="testing review again"
# studentCourse3.rating=3
# studentCourse4.review="testing review still"
# studentCourse4.rating=4
# studentCourse5.review="testing review done"
# studentCourse5.rating=5

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