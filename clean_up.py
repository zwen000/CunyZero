import os
import sys
import shutil

from cunyzero import db, bcrypt
from cunyzero.models import *


file = "./cunyzero/database.db"


if os.path.isfile(file):
    os.remove(file)                             # Deletes the old 'database.db' file if it exists.
else:
    print("Error: %s file not found" % file)

shutil.rmtree("./cunyzero/__pycache__")         # Deletes '__pycache__' directory and all its contents.


db.create_all()                                 # Create the new 'database.db' file from 'models.py'

user = User(username='admin', password=bcrypt.generate_password_hash('admin').decode('utf-8'), role='Admin')
student = User(username='student', password=bcrypt.generate_password_hash('student').decode('utf-8'), role='Student')
instructor = User(username='instructor', password=bcrypt.generate_password_hash('instructor').decode('utf-8'),
                  role='Instructor')
db.session.add(user)
db.session.add(student)
db.session.add(instructor)
# programs creation
program1 = Program(id=1, name="Bacholor of Computer Science")
db.session.add(program1)

db.session.commit()