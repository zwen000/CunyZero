from flask import render_template, url_for, flash, redirect, request
from cunyzero import app, db, bcrypt
from cunyzero.forms import *
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
    if current_user.role == 'Student':
        owner = current_user.studentOwner
    elif current_user.role == 'Instructor':
        owner = current_user.instructorOwner
    else:
        owner = current_user.adminOwner

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
                           image_file=image_file, form=form, owner=owner)


@login_required
@app.route('/application/')
def enrollment_application():
    return render_template("enrollment-application.html", title="Visitor-Application")


@login_required
@app.route('/application/student', methods=['GET', 'POST'])
def student_application():#If you are not logged in and goto /application/student there will be attributeerror
    form = ApplicationForm()
    application = Application.query.filter_by(approval=None, visitor_id=current_user.ownerId).first()
    if application:
        flash(f'You have an application processing!', 'danger')
        return redirect(url_for('enrollment_application'))
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
        return redirect(url_for('enrollment_application'))

    return render_template("student-application.html", title="Student Application", form=form)


@login_required
@app.route('/application/instructor', methods=['GET', 'POST'])
def instructor_application():
    form = InstructorApplicationForm()
    application_exited = Application.query.filter_by(approval=None, visitor_id=current_user.ownerId).first()
    if application_exited:
        flash(f'You have an application processing!', 'danger')
        return redirect(url_for('enrollment_application'))
    if form.validate_on_submit():
        application = Application(visitor_id=current_user.visitorOwner.ownerId, firstname=form.firstname.data,
                                          lastname=form.lastname.data, intro=form.intro.data,
                                          type='Instructor')
        print("inst  ", application)
        db.session.add(application)
        db.session.commit()
        flash(f'Your application id: {current_user.ownerId} is submitted successfully!', 'success')
        return redirect(url_for('enrollment_application'))
    return render_template("instructor-application.html", title="Instructor Application", form=form)


# Admin only
@login_required
@app.route('/application/list', methods=['GET', 'POST'])
def application_manage():
    applications = Application.query.filter_by(approval=None)
    return render_template("application-manage.html", title="Application-List", applications=applications)


@login_required
@app.route('/application/<int:application_id>', methods=['GET', 'POST'])
def application_confirm(application_id):
    form = ApplicationReviewForm()
    application = Application.query.get(application_id)
    user = application.applicant.user[0]
    if form.validate_on_submit():
        if form.accept.data:
            application.approval = True
            application.justification = form.justification.data
            if application.type == "Student":
                program = Program.query.filter_by(name= application.program_name).first()
                program.enrolled_total += 1
                student = Student(ownerId=random.randint(20000001, 30000000),
                                  programId=program.id,
                                  firstname=application.firstname,
                                  lastname=application.lastname,
                                  gpa=application.GPA)
                db.session.add(student)
                user.role = "Student"
                user.ownerId = student.ownerId
            else:
                instructor = Instructor(ownerId=random.randint(30000001, 40000000),
                                        firstname=application.firstname,
                                        lastname=application.lastname
                                        )
                db.session.add(instructor)
                user.role = "Instructor"
                user.ownerId = instructor.ownerId

            db.session.commit()
            flash(f'{application.type} Application for ({application.firstname}'
                  f' {application.lastname}) has been accepted!', 'success')
            return redirect(url_for('application_manage'))
        if form.reject.data:
            if form.justification.data != '':
                application.approval = False
                application.justification = form.justification.data
                db.session.commit()

                flash(f'{application.type} Application for ( {application.firstname}'
                      f' {application.lastname}) has been rejected!', 'danger')
                return redirect(url_for('application_manage'))
            else:
                flash(f'Please provide your reason!', 'danger')
    return render_template("application-confirm.html", title="Application-Confirm", form=form,
                           application=application)


# Student only
#@login_required
@app.route('/course/register', methods=['GET', 'POST'])
def register_course():
    if current_user.role != "Student":
        return redirect(url_for('home'))
    
    # courses = Course.query.filter_by(status="Open")
    # studentCourses = StudentCourse.query.filter_by(studentId=current_user.ownerId)
    # courseIds = [sc.courseId for sc in studentCourses]# id of courses student enrolled/waitlisted in
    # enrolledIds = [sc.courseId for sc in studentCourses if not sc.waiting]# id of courses student enrolled in

    # notEnrolledCourses = [course for course in courses if course.id not in courseIds]
    # enrolledCourses = [course for course in courses if course.id in enrolledIds]
    # waitListedCourses = [course for course in courses if (course.id in courseIds) and (course.id not in enrolledIds)]

    courseId = request.form.get("Enroll")
    if courseId:# Attempting to Enroll In a Course
        courseId = int(courseId)
        course = Course.query.filter_by(id=courseId).first()
        #courseSize = len(StudentCourse.query.filter_by(courseId=courseId, waiting=False))
        courseSize = 0#len dont seem to work
        for i in StudentCourse.query.filter_by(courseId=courseId, waiting=False):
            if i:
                courseSize+=1
        if course.courseConflict(current_user.ownerId):
            flash(f'Course {course.coursename}, has conflict with enrolled course!','danger')
        else:
            if courseSize<course.capacity:# if course not full
                studentcourse = StudentCourse(courseId=courseId, studentId=current_user.ownerId, waiting=False)
                db.session.add(studentcourse)
                db.session.commit()
                flash(f'You have successfully enrolled in {course.coursename}','success')
            else:# course full
                #waitListSize = len(StudentCourse.query.filter_by(courseId=courseId, waiting=True))
                waitListSize = 0
                for i in StudentCourse.query.filter_by(courseId=courseId, waiting=True):
                    if i:
                        waitListSize+=1
                if waitListSize<course.waitListCapacity:# if waitlist not full
                    studentcourse = StudentCourse(courseId=courseId, studentId=current_user.ownerId, waiting=True)
                    db.session.add(studentcourse)
                    db.session.commit()
                    flash(f'You are now waitlisted for {course.coursename}','warning')
                else:
                    flash('Course is full','danger')

    courseId = request.form.get("Drop")
    if courseId:# Dropping a Course
        courseId = int(courseId)
        StudentCourse.query.filter_by(courseId=courseId, studentId=current_user.ownerId).delete()
        db.session.commit()
        flash(f'You have successfully dropped a course','success')

    student = Student.query.filter_by(ownerId=current_user.ownerId).first()
    # return render_template("register-course.html", courses=student.notEnrolled(), 
    #                                                 enrolled = student.enrolled(), 
    #                                                 waitListed = student.waitListed())
    # student = current_user.studentOwner
    return render_template("register-course.html", student=student)


# Admin only
#@login_required
@app.route('/course/create', methods=['GET', 'POST'])
def create_course():
    # if current_user.role != "Admin":
    #     return redirect(url_for('home'))
    form = CreateCourseForm()
    if form.validate_on_submit():
        dayofweek = ""
        for i in form.dayofweek.data:
            dayofweek+=i
        course = Course(instructorId=form.instructor.data[0].ownerId, dayofweek=dayofweek, coursename=form.coursename.data,
                        startPeriod=form.startPeriod.data, endPeriod=form.endPeriod.data,
                        capacity=form.capacity.data, waitlist_capacity=form.waitListCapacity.data)
        db.session.add(course)
        db.session.commit()
        flash(f'You have successfully created new course {course.coursename}', 'success')
        return redirect(url_for("course_manage"))
    return render_template("create-course.html", form=form)


@login_required
@app.route('/student/list', methods=['GET', 'POST'])
def student_manage():
    students = Student.query.all()
    programs = Program.query.all()
    return render_template("student-manage.html", title="Student Management", students=students, programs=programs)


@login_required
@app.route('/instructor/list', methods=['GET', 'POST'])
def instructor_manage():
    instructors = Instructor.query.all()
    return render_template("instructor-manage.html", title="Instructor Management", instructors=instructors)


@login_required
@app.route('/<string:role>/<int:owner_id>', methods=['GET', 'POST'])
def individual_review(role, owner_id):
    form = WarningForm()
    if form.validate_on_submit():
        warning = Warning(userId=owner_id, message=form.message.data)
        db.session.add(warning)
        db.session.commit()
        flash(f'The warning for Student id: {warning.userId} is submitted, reason is {form.message.data }!', 'success')
        return redirect(url_for("individual_review", role=role, owner_id=owner_id))

    if role == "Student":
        student = Student.query.get(owner_id)
        program = Program.query.filter_by(id=student.programId).first()
        user = student.user[0] # find the student account's user
        student_courses = student.courses # by relationship student.courses
        courses = []
        for student_course in student_courses:
            course = Course.query.get(student_course.courseId)
            courses.append(course)
        return render_template("individual-review.html", title="Student Review", owner=student, user=user,
                               program=program, courses=courses, form=form)
    if role == "Instructor":
        instructor = Instructor.query.get(owner_id)
        user = instructor.user[0]
        courses = Course.query.filter_by(instructorId=owner_id)
        return render_template("individual-review.html", title="Instructor Review", owner=instructor, user=user,
                               courses=courses, form=form)


@login_required
@app.route('/course/list', methods=['GET', 'POST'])
def course_manage():
    current_courses = Course.query.filter_by(status="Open")
    past_courses = Course.query.filter_by(status="Finished")
    courseId = request.form.get("Cancel")
    if courseId:
        courseId = int(courseId)
        course = Course.query.get(courseId)
        # course can only safe delete when the it don't have any students,
        if course.getEnrolledTotal() == 0:
            db.session.delete(course)
            db.session.commit()
            flash(f'The course {course.coursename} is deleted successfully', 'success')
            return redirect(url_for("course_manage"))
        else:
            flash(f'The course {course.coursename} can\'t be deleted since there are students registered!', 'danger')
            return redirect(url_for("course_manage"))
    return render_template("course_manage.html", title="Course Management", current_courses=current_courses,
                           past_courses=past_courses)


@login_required
@app.route('/complaint/list', methods=['GET', 'POST'])
def complaint_manage():
    unprocessed_comp = Complaint.query.filter_by(processed=False)
    processed_comp = Complaint.query.filter_by(processed=True)
    return render_template("complaint-manage.html", title="Complaint Management", unprocessed_comp=unprocessed_comp,
                           processed_comp=processed_comp)


