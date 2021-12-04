from operator import truediv
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
    if current_user.studentOwner.status=='Suspended':
        flash("No access, You are suspended!", 'danger')
        return redirect(url_for('home'))
    period = Period.query.all()[0]
    courseId = request.form.get("Enroll")
    if courseId:# Attempting to Enroll In a Course
        courseId = int(courseId)
        course = Course.query.filter_by(id=courseId).first()
        courseSize = StudentCourse.query.filter_by(courseId=courseId, waiting=False).count()
        enrolledCourseCount = StudentCourse.query.filter_by(courseId=courseId, studentId=current_user.ownerId, waiting=False).count()
        if period.getPeriodName!= "" and not current_user.studentOwner.enrollmentPermission:
            flash('Not course registration period and no special permission to enroll!', 'danger')
        else:
            if enrolledCourseCount == 4:
                flash('Already enrolled in 4, the maximum number of courses!', 'danger')
            else:
                prevCourse = StudentCourse.query.filter_by(courseId=courseId, studentId=current_user.ownerId).first()
                if prevCourse.gpa and prevCourse.gpa!='F':# if student already has a non f grade
                    flash(f'Course {course.coursename} already taken with grade {prevCourse.gpa}!','danger')
                else:
                    if course.courseConflict(current_user.ownerId): 
                        flash(f'Course {course.coursename}, has conflict with enrolled course!','danger')
                    else:
                        if courseSize<course.capacity:# if course not full
                            studentcourse = StudentCourse(courseId=courseId, studentId=current_user.ownerId, waiting=False)
                            db.session.add(studentcourse)
                            db.session.commit()
                            flash(f'You have successfully enrolled in {course.coursename}','success')
                        else:# course full
                            waitListSize = StudentCourse.query.filter_by(courseId=courseId, waiting=True).count()
                            if waitListSize<course.waitListCapacity:# if waitlist not full
                                studentcourse = StudentCourse(courseId=courseId, studentId=current_user.ownerId, waiting=True)
                                db.session.add(studentcourse)
                                db.session.commit()
                                flash(f'You are now waitlisted for {course.coursename}','warning')
                            else:
                                flash('Course is full','danger')

    courseId = request.form.get("Drop")
    if courseId:# Dropping a Course
        periodName = period.getPeriodName()
        courseId = int(courseId)
        sc = StudentCourse.query.filter_by(courseId=courseId, studentId=current_user.ownerId)
        if periodName == "Course Registration Period" or sc.first().waiting==True:# registration period or waitlisted class, delete class
            sc.delete()
            flash(f'You have successfully dropped a course','success')
        elif periodName == "Course Running Period" or period =="Grading Period":# running-grading period, drop with grade w
            StudentCourse.query.filter_by(courseId=courseId, studentId=current_user.ownerId, waiting=False).first().gpa = 'W'
            flash(f'You have dropped a course with grade W','success')
        else:
            flash(f'Cannot Drop Course!','danger')
        db.session.commit()

    student = Student.query.filter_by(ownerId=current_user.ownerId).first()
    return render_template("register-course.html", student=student)

# Admin only
#@login_required
@app.route('/course/create', methods=['GET', 'POST'])
def create_course():
    if current_user.role != "Admin":
        return redirect(url_for('home'))
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
    return render_template("course-manage.html", title="Course Management", current_courses=current_courses,
                           past_courses=past_courses)


@login_required
@app.route('/complaint/list', methods=['GET', 'POST'])
def complaint_manage():
    unprocessed_comp = Complaint.query.filter_by(processed=False)
    processed_comp = Complaint.query.filter_by(processed=True)
    return render_template("complaint-manage.html", title="Complaint Management", unprocessed_comp=unprocessed_comp,
                           processed_comp=processed_comp)


# admin and instructor able to use this page to see the detail information of course
# such as student in the course, and student grade, etc...
# if grade is not assigned, and current period is grade period, instructor are able to give the grade to each
@login_required
@app.route('/course/<int:course_Id>', methods=['GET', 'POST'])
def course_review(course_Id):
    course = Course.query.get(course_Id)
    programs = Program.query.all()
    students = db.session.query(Student, StudentCourse)\
        .join(StudentCourse, StudentCourse.studentId == Student.ownerId).filter(StudentCourse.courseId == course_Id,
                                                                                StudentCourse.waiting == False).all()
    students_waitlist = db.session.query(Student, StudentCourse)\
        .join(StudentCourse, StudentCourse.studentId == Student.ownerId).filter(StudentCourse.courseId == course_Id,
                                                                                StudentCourse.waiting == True).all()
    return render_template("course-review.html", title="Course Detail Review", course=course, students=students,
                           programs=programs, students_waitlist=students_waitlist)


@app.route('/test', methods=['GET', 'POST'])
def test():

    student = db.session.query(Student, StudentCourse).join(StudentCourse, StudentCourse.studentId == Student.ownerId).filter(StudentCourse.courseId == 38239413).all()
    return student[0].Student.firstname + student[0].Student.lastname + str(student[0].StudentCourse.courseId)

# Admin only
#@login_required
@app.route('/admin/period', methods=['GET', 'POST'])
def change_period():
    if current_user.role != "Admin":
        return redirect(url_for('home'))

    form = SystemForm()
    period = Period.query.all()[0]
    admin = Admin.query.all()[0]
    if form.validate_on_submit():
        if form.updateTaboo.data:
            admin.taboo_list = form.taboo_list.data
            db.session.commit()
        if form.nextPeriod.data:
            period.advancePeriod()#advance to next period and do the task logic
    elif request.method=='GET':
        form.taboo_list.data = admin.taboo_list
    
    return render_template("change-period.html", form=form, period=period)

#student and instructor only
#@login_required
@app.route('/warning/<int:userId>', methods=['GET', 'POST'])
def user_warning_page(userId):# show all warnings for that user
    if (current_user.role!='Student' and current_user.role!='Instructor') or (userId != current_user.ownerId):
        return redirect(url_for('home'))

    warnings = Warning.query.filter_by(userId=userId)
    return render_template("user-warning.html", warnings=warnings)

#admin only
#@login_required
@app.route('/admin/review-warning', methods=['GET', 'POST'])
def review_warning_page():#show all warnings admin need to review
    if current_user.role!="Admin":
        return redirect(url_for('home'))
    form = JustifyWarningForm()
    warnings = Warning.query.all()
    #get warnings with justification from users and with no result/judgement from admin
    warningsWithJustification = [warning for warning in warnings if warning.justification!='' and warning.result=='']
    return render_template("user-warning.html", form=form, warnings=warningsWithJustification)

#@login_required
@app.route('/warning/<int:userId>/<int:warningId>', methods=['GET', 'POST'])
def warning_page(userId, warningId):# show specific warning
    if current_user.role!='Admin':
        if (current_user.role!='Student' and current_user.role!='Instructor') or (userId != current_user.ownerId):
            return redirect(url_for('home'))

    form = JustifyWarningForm()
    user = User.query.filter_by(ownerId=userId).first()
    owner = (user.studentOwner if user.role=='Student' else user.instructorOwner)
    warning = Warning.query.filter_by(id=warningId, userId=userId).first()
    program = (Program.query.filter_by(id=owner.programId).first() if user.role=='Student' else None)
    
    if form.validate_on_submit():
        if current_user.role=='Admin':
            if warning.result == '':
                if form.accept.data:
                    warning.result = "Justification Accepted, Warning -1"
                    owner.warning-=1
                    flash("Justification Accepted",'success')
                elif form.reject.data:
                    warning.result = "Justification Rejected"
                    flash("Justification Rejected",'success')
            else:
                flash("Already Processed",'danger')
        else:
            warning.justification=form.justification.data
            flash("Justification Updated",'success')
        db.session.commit()
    elif request.method=='GET': 
        form.justification.data = warning.justification

    return render_template("review-warning.html", form=form, warning=warning, owner=owner, user=user, program=program)

#@login_required
@app.route('/course/review/<int:courseId>', methods=['GET', 'POST'])
def course_rating(courseId):#show all ratings for the course
    if not current_user.is_authenticated:
        return redirect(url_for('home'))
    reviews = StudentCourse.query.filter_by(courseId=courseId)
    return render_template("course-rating.html", reviews=reviews, courseId=courseId)

#only for user who posted review
#@login_required
@app.route('/course/review/<int:courseId>/<int:studentId>', methods=['GET', 'POST'])
def update_rating(courseId, studentId):#show specific rating
    if not current_user.is_authenticated:
        return redirect(url_for('home'))
    if current_user.ownerId!=studentId:
        return redirect(url_for('course_rating',courseId=courseId))

    form = ReviewForm()
    user = User.query.filter_by(ownerId=studentId).first()
    owner = Student.query.filter_by(ownerId=studentId).first()
    review = StudentCourse.query.filter_by(courseId=courseId, studentId=studentId).first()
    period = Period.query.all()[0].getPeriodName()
    if review.waiting==True:
        flash("cannot leave review for waitlisted course!",'danger')
        return redirect(url_for('course_rating',courseId=courseId))
    if form.submit.data:
        if period=="Course Running Period" or period=="Grading Period":
            if not review.gpa:
                review.review=form.content.data
                review.rating=form.rating.data
                db.session.commit()
                flash("Review Updated", "success")
            else:
                flash("GPA is out, reviews can no longer be written!", 'danger')
        else:
            flash("Reviews can only be submitted from running to grading period!", 'danger')
    elif request.method=='GET':
        form.content.data=review.review
        form.rating.data=review.rating

    if review:
        return render_template("rating.html", form=form, review=review, owner=owner, user=user)
    else:
        return redirect(url_for('course_rating',courseId=courseId))