from flask import render_template, url_for, flash, redirect, request
from cunyzero import app, db, bcrypt
from cunyzero.forms import RegistrationForm, LoginForm, UpdateAccountForm, ApplicationForm, ConfirmForm
from cunyzero.models import *
from flask_login import login_user, current_user, logout_user, login_required
from flask_user import roles_required, SQLAlchemyAdapter, UserManager, UserMixin
import secrets
import random
import os
from PIL import Image

highest_rate_course = [
    {
        'course_name': 'csc 32200',
        'instructor': 'Prof. X',
        'status': 'Current',
        'rate': '5 star'
    }
]

lowest_rate_course = [
    {
        'course_name': 'csc 33200',
        'instructor': 'Prof. Y',
        'Status': 'Finished',
        'rate': '0 star'
    }
]

highest_GPA_student = [
    {
        'student': 'Corey Schafer',
        'major_in': 'Computer Science',
        'status': 'senior',
        'gpa': '4.0'
    }
]

posts = [
    {
        'author':  'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First Post Content',
        'date_posted': 'April 20, 2018'
    }
]


@app.route('/')
@app.route('/home')
def home():
    return render_template("home.html", highest_rate_course=highest_rate_course, lowest_rate_course=lowest_rate_course,
                           highest_GPA_student=highest_GPA_student)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        visitor = Visitor(ownerId=random.randint(10000000, 20000000))
        user.ownerId = visitor.ownerId
        db.session.add(visitor)
        db.session.add(user)
        db.session.commit()

        flash(f'Your account has been created for {form.username.data}! You are now able to log in', 'success')
        return redirect(url_for('login'))

    return render_template("register.html", title="Register", form=form)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        print(form.submit.data)
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login Successful!', 'success')
            next_page = request.args.get('next')

            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password!', 'danger')
    return render_template("login.html", title="Login", form=form)


@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    logout_user()
    flash('Your account is logged out', 'success')
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    # resize
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path) #save the picture in picture_path
    return picture_fn


@app.route('/account/', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        # if form.picture.data:
        #     picture_file = save_picture(form.picture.data)
        #     current_user.image_file = picture_file
        if form.password.data:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            current_user.password = hashed_password
        current_user.username = form.username.data
        current_user.firstname = form.firstname.data
        current_user.lastname = form.lastname.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username

    image_file = url_for('static', filename= "profile_pics/" + current_user.image_file)
    return render_template("account.html", title="Account",
                           image_file=image_file, form=form)


@login_required
@app.route('/application/')
def application():
    return render_template("application.html", title="Visitor-Application")


@login_required
@app.route('/application/student', methods=['GET', 'POST'])
def student_application():
    form = ApplicationForm()
    application = Application.query.filter_by(approval=None, visitor_id=current_user.ownerId).first()
    if application:
        flash(f'You have an application processing!', 'danger')
        return redirect(url_for('application'))
    if form.validate_on_submit():

        selected_program = None
        for i in form.program.data:
            selected_program = i.name
        application = Application(visitor_id=current_user.visitorOwner.ownerId, firstname=form.firstname.data,
                                          lastname=form.lastname.data, intro=form.intro.data,
                                          type='Student', GPA=float(form.GPA.data), program_name=selected_program)
        db.session.add(application)
        db.session.commit()
        flash(f'Your application with id: {current_user.ownerId} is submitted successfully!', 'success')
        return redirect(url_for('application'))

    return render_template("student-application.html", title="Student Application", form=form)


@login_required
@app.route('/application/instructor', methods=['GET', 'POST'])
def instructor_application():
    form = ApplicationForm()
    application = Application.query.filter_by(approval=None, visitor_id=current_user.ownerId).first()
    if application:
        flash(f'You have an application processing!', 'danger')
        return redirect(url_for('application'))
    if form.validate_on_submit():
        application = Application(visitor_id=current_user.visitorOwner.ownerId, firstname=form.firstname.data,
                                          lastname=form.lastname.data, intro=form.intro.data,
                                          type='Instructor')
        db.session.add(application)
        db.session.commit()
        flash(f'Your application id: {current_user.ownerId} is submitted successfully!', 'success')
        return redirect(url_for('application'))
    return render_template("instructor-application.html", title="Instructor Application", form=form)


def list_validate_on_submit(forms):
    for form in forms:
        if form.validate_on_submit:
            return form.validate_on_submit
        else:
            continue
    return None;

# Admin only
@login_required
@app.route('/confirm/', methods=['GET', 'POST'])
def confirm():
    applications = Application.query.filter_by(approval=None)
    forms = []
    for current_application in applications:
        form = ConfirmForm()
        form.id.data = current_application.id
        forms.append(form)
        if form.validate_on_submit():
            if form.accept.data:
                current_application.approval = True
                current_application.justification = form.justification.data
                db.session.commit()
                flash(f'Application with type ({current_application.type}: {current_application.firstname}'
                      f' {current_application.lastname}) has been accepted!', 'success')
                return redirect(url_for('confirm'))
            if form.reject.data:
                if form.justification.data != '':
                    current_application.approval = False
                    current_application.justification = form.justification.data
                    db.session.commit()
                    flash(f'Application with ({current_application.type}: {current_application.firstname}'
                          f' {current_application.lastname}) has been rejected!', 'success')
                    return redirect(url_for('confirm'))
                else:
                    flash(f'Please provide your reason!', 'danger')
                    return redirect(url_for('confirm'))
    index = len(forms)
    return render_template("confirm.html", title="Visitor-Application-confirm", applications=applications, index=index,
                           forms=forms)




