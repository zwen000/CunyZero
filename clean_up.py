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
student = Student(ownerId=random.randint(20000001, 30000000), programId=1, firstname="f", lastname="l")
instructor = Instructor(ownerId=random.randint(30000001, 40000000),  firstname="f", lastname="l")

user1 = User(username='admin', password=bcrypt.generate_password_hash('admin').decode('utf-8'), role='Admin')
user2 = User(username='student', password=bcrypt.generate_password_hash('student').decode('utf-8'), role='Student')
user3 = User(username='instructor', password=bcrypt.generate_password_hash('instructor').decode('utf-8'),
                  role='Instructor')

user1.ownerId = admin.ownerId
user2.ownerId = student.ownerId
user3.ownerId = instructor.ownerId

db.session.add(student)
db.session.add(instructor)
db.session.add(admin)
db.session.add(user1)
db.session.add(user2)
db.session.add(user3)

#testing courses
course1 = Course(id=random.randint(10000000, 20000000), instructorId=user3.ownerId, dayofweek="MoTuWe", coursename="Cs322",
                startPeriod="1", endPeriod="9")
course2 = Course(id=random.randint(20000001, 30000000), instructorId=user3.ownerId, dayofweek="Sa", coursename="Cs5000",
                startPeriod="3", endPeriod="4")
course3 = Course(id=random.randint(30000001, 40000000), instructorId=user3.ownerId, dayofweek="Su", coursename="Cs300",
                startPeriod="3", endPeriod="4")
course4 = Course(id=random.randint(40000001, 50000000), instructorId=user3.ownerId, dayofweek="TuThFr", coursename="Cs50",
                startPeriod="3", endPeriod="4")
course5 = Course(id=random.randint(50000001, 60000000), instructorId=user3.ownerId, dayofweek="TuThFr", coursename="Cs212",
                startPeriod="5", endPeriod="6")

db.session.add(course1)
db.session.add(course2)
db.session.add(course3)
db.session.add(course4)
db.session.add(course5)

studentCourse2 = StudentCourse(courseId = course2.id, studentId = user2.ownerId, waiting = True)
studentCourse3 = StudentCourse(courseId = course3.id, studentId = user2.ownerId, waiting = True)
studentCourse4 = StudentCourse(courseId = course4.id, studentId = user2.ownerId, waiting = False)
studentCourse5 = StudentCourse(courseId = course5.id, studentId = user2.ownerId, waiting = False)

db.session.add(studentCourse2)
db.session.add(studentCourse3)
db.session.add(studentCourse4)
db.session.add(studentCourse5)

#testing period
period = Period(period=2)#course grading period
db.session.add(period)

#testing review
studentCourse2.review="testing review"
studentCourse2.rating=2
studentCourse3.review="testing review again"
studentCourse3.rating=3
studentCourse4.review="testing review still"
studentCourse4.rating=4
studentCourse5.review="testing review done"
studentCourse5.rating=5

db.session.commit()

# #testing warnings/period
# period.advanceNPeriod(50)# advances period 50 times and perform the task logic, warnings will be given accordingly

# warnings = Warning.query.all()
# if len(warnings)>=10:
#     for i in range(10):
#         warnings[i].justification="some justification"
# db.session.commit()
