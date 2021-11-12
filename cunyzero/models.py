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

    posts = db.relationship('Post', backref='author', lazy=True)
    role = db.Column(db.String(30), nullable=False, default='Visitor')
    ownerId = db.Column(db.Integer, db.ForeignKey('visitor.ownerId'), db.ForeignKey('admin.ownerId'))

    def __repr__(self):
        return f"User('{self.username}')"

class Admin(db.Model): #Admin.user, User.adminOwner
    ownerId = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    user = db.relationship('User', backref='adminOwner', lazy=True)

    def __repr__(self):
        return f"Admin('{self.ownerId}')"

class Visitor(db.Model):
    ownerId = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    user = db.relationship('User', backref='visitorOwner', lazy=True)
    applications = db.relationship('Application', backref='applicant', lazy=True)

    def __repr__(self):
        return f"Visitor('{self.ownerId}')"

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(30), nullable=False)
    lastname = db.Column(db.String(30), nullable=False)
    intro = db.Column(db.Text, nullable=False) # self introduction
    visitor_id = db.Column(db.Integer, db.ForeignKey('visitor.ownerId'), nullable=False)
    program_name = db.Column(db.String(20), db.ForeignKey('program.name'), nullable=False)

    # for student only
    GPA = db.Column(db.Integer, unique=False, nullable=False, default=0)

    # For registrar Use
    justification = db.Column(db.Text, nullable=False, default='')
    approval = db.Column(db.Boolean,  default=None)   # None: waiting for registrar to make decision


class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False, default=5)
    enrolled_total = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"Program('{self.id}', '{self.name}', '{self.enrolled_total}', '{self.capacity}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}, {self.date_posted}')"