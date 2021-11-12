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
db.session.add(user)

# admin = Admin()
# db.session.add(admin)

db.session.commit()