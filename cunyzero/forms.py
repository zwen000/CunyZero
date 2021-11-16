from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms.fields import StringField, PasswordField, SubmitField, BooleanField, SelectField, DecimalField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Optional
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
    application_type = StringField('Application type')
    firstname = StringField('Firstname', validators=[DataRequired()])
    lastname = StringField('Lastname', validators=[DataRequired()])
    intro = StringField('Self-Description')
    GPA = DecimalField('GPA', validators=[Optional()])
    program = StringField('Program', validators=[Optional()])
    submit = SubmitField('Send Application')
