from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_login import current_user
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
    GPA = DecimalField('GPA', validators=[DataRequired()])
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
        get_label='ownerId'
    )                                
    startPeriod = IntegerField('Start Period', validators=[DataRequired(), NumberRange(min=1,max=9)])
    endPeriod = IntegerField('End Period', validators=[DataRequired(), NumberRange(min=1,max=9)])
    capacity = IntegerField('Capacity', validators=[DataRequired(), NumberRange(min=5,max=100)])
    waitListCapacity = IntegerField('Wait List Capacity', validators=[DataRequired(), NumberRange(min=0,max=100)])
    submit = SubmitField('Create')

    def validate_coursename(self, coursename):
            course = Course.query.filter_by(course_name=coursename.data).first()
            if course:
                raise ValidationError("That coursename is taken, Please choose a different one.")


class WarningForm(FlaskForm):
    message = TextAreaField('Warning message: ', validators=[DataRequired()])
    submit = SubmitField('Confirm')


class GraduationForm(FlaskForm):
    FirstName= StringField('FirstName',validators=[DataRequired(),Length(min=2,max=20)])
    LastName= StringField('LastName',validators=[DataRequired(),Length(min=2,max=20)])
    GPA = DecimalField('GPA', validators=[DataRequired()])
    Major=StringField('Major',validators=[DataRequired(),Length(min=2,max=30)])
    submit= SubmitField('Submit')
   

