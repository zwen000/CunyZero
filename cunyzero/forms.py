from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_login import current_user
from werkzeug.datastructures import Accept
from wtforms import *
from wtforms.fields import *
from wtforms_sqlalchemy.fields import *
from wtforms.validators import DataRequired, Length, EqualTo, NumberRange, ValidationError, Optional
from cunyzero.models import *


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)] )
    password = PasswordField('Password', validators=[DataRequired()] )
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password') ])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("That username is taken, Please choose a different one.")


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()] )
    password = PasswordField('Password', validators=[DataRequired()])
    # remember by cookie
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    firstname = StringField('Firstname', validators=[DataRequired()])
    lastname = StringField('Lastname', validators=[DataRequired()])
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)] )
    password = PasswordField('Password', validators=[DataRequired()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("That username is taken, Please choose a different one.")


class ApplicationForm(FlaskForm):
    firstname = StringField('Firstname', validators=[DataRequired()])
    lastname = StringField('Lastname', validators=[DataRequired()])
    intro = TextAreaField('Self-Description', default="", validators=[Length(0, 300)])
    GPA = DecimalField('GPA', validators=[DataRequired(), NumberRange(min=0,max=4.0)])
    program = QuerySelectMultipleField(
        'Program',
        allow_blank=True,
        query_factory = lambda: Program.query,
        widget=widgets.Select(multiple=False),
        get_label='name'
    )
    submit = SubmitField('Send Application')

class InstructorApplicationForm(FlaskForm):
    firstname = StringField('Firstname', validators=[DataRequired()])
    lastname = StringField('Lastname', validators=[DataRequired()])
    intro = TextAreaField('Self-Description', default="", validators=[Length(0, 300)])

    submit = SubmitField('Send Application')

class ApplicationReviewForm(FlaskForm):
    id = StringField('Application ID', validators=[DataRequired()])
    justification = TextAreaField('Give A Justification: ')
    accept = SubmitField('Accept')
    reject = SubmitField('Reject')

class CreateCourseForm(FlaskForm):
    coursename = StringField('Coursename',
                            validators=[DataRequired(), Length(min=2, max=20)])
    dayofweek = SelectMultipleField(
        'Days of the Week', 
        validators=[DataRequired()], 
        choices=[("Mo", "Mo"),("Tu", "Tu"),("We", "We"),("Th", "Th"),("Fr", "Fr"),("Sa", "Sa"),("Su", "Su")],
        widget = widgets.ListWidget(prefix_label=False),
        option_widget = widgets.CheckboxInput()
    )
    instructor = QuerySelectMultipleField(
        'Instructors',
        validators=[DataRequired()], 
        query_factory = lambda: Instructor.query,
        widget=widgets.Select(multiple=False),
        get_label=lambda instructor: f"{instructor.ownerId}: {instructor.firstname} {instructor.lastname}"
    )                                
    startPeriod = IntegerField('Start Period', validators=[DataRequired(), NumberRange(min=1,max=9)])
    endPeriod = IntegerField('End Period', validators=[DataRequired(), NumberRange(min=1,max=9)])
    capacity = IntegerField('Capacity', validators=[DataRequired(), NumberRange(min=5,max=100)])
    waitListCapacity = IntegerField('Wait List Capacity', validators=[DataRequired(), NumberRange(min=0,max=100)])
    submit = SubmitField('Create')

    def __init__(self, myParam: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.period = myParam

    def validate_coursename(self, coursename):
            course = Course.query.filter_by(coursename=coursename.data, creationPeriod=self.period).first()
            if course:
                raise ValidationError("That coursename is taken, Please choose a different one.")


class WarningForm(FlaskForm):
    # the targetId will change to current reviewed people id by get method when first time open the routes
    message = QuerySelectMultipleField(
        'Complaint message',
        validators=[DataRequired()],
        query_factory = lambda: Complaint.query,
        widget=widgets.Select(multiple=False),
        get_label='message'
    )
    submit2 = SubmitField('Confirm')
    def __init__(self, myParam: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.targetId = myParam
        self.message.query_factory = lambda:Complaint.query.filter(Complaint.targetId == self.targetId,
                                                                   Complaint.processed == 0).all()

class DeregisterForm(FlaskForm):
    courseId = IntegerField('Course', validators=[DataRequired()], render_kw={'readonly': True})
    message = QuerySelectMultipleField(
        'Complaint message',
        validators=[DataRequired()],
        query_factory = lambda : Complaint.query,
        widget=widgets.Select(multiple=False),
        get_label='message',
    )
    submit3 = SubmitField('Confirm')
    def __init__(self, myParam: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.targetId = myParam
        self.message.query_factory = lambda:Complaint.query.filter(Complaint.targetId == self.targetId,
                                                                   Complaint.processed == 0).all()

class GraduationForm(FlaskForm):
    submit1=SubmitField('Apply for Graduation')

class SystemForm(FlaskForm):
    taboo_list = TextAreaField('Taboo List')
    updateTaboo = SubmitField('Update')
    nextPeriod = SubmitField('Advance')

class JustifyWarningForm(FlaskForm):
    #for student/instructor
    justification = TextAreaField('Provide Justification')
    provideJustification = SubmitField('Update')
    
    #for admin
    accept = SubmitField('Accept')
    reject = SubmitField('Reject') 


class ReviewForm(FlaskForm):
    rating = IntegerField('Rating', validators=[DataRequired(), NumberRange(min=1,max=5)])
    content = TextAreaField('Review', validators=[DataRequired()])
    submit = SubmitField('Update')


class InstructorComplaintForm(FlaskForm):
    target = QuerySelectMultipleField(
        'Choose a Student',
        query_factory = lambda: Student.query,
        widget=widgets.Select(multiple=False),
        get_label= lambda student: f"{student.ownerId} -- {student.firstname} {student.lastname}"
    )
    # reason = RadioField('Reason', choices=[('Warning','Warn the student'),('De-Register','De-Register the student'), ('Other', 'Other')], default='Warning', validators=[DataRequired()])
    message = TextAreaField('Detail', validators=[DataRequired()])
    submit = SubmitField('Submit')


class StudentComplaintForm(FlaskForm):
    target = QuerySelectMultipleField(
        'Choose a Student or Instructor',
        query_factory= lambda: User.query.filter((User.role!="Visitor")&(User.role!="Admin")&(User.id!=current_user.id)),
        widget=widgets.Select(multiple=False),
        get_label=lambda user: f'{user.role}, {user.ownerId}, '
                               f'{user.studentOwner.firstname + " " + user.studentOwner.lastname if user.role == "Student" else user.instructorOwner.firstname + " " + user.instructorOwner.lastname}'
    )

    message = TextAreaField('Detail', validators=[DataRequired()])
    submit = SubmitField('Submit')