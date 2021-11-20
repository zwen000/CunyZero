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




db.session.commit()