from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import *
from wtforms.fields import *
from wtforms_sqlalchemy.fields import *
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
    firstname = StringField('Firstname', validators=[DataRequired()])
    lastname = StringField('Lastname', validators=[DataRequired()])
    intro = TextAreaField('Self-Description', default="", validators=[Length(0, 300)])
    GPA = DecimalField('GPA', validators=[DataRequired()])
    program = QuerySelectMultipleField(
        'Program',
        #allow_blank=True,
        query_factory = lambda: Program.query,
        widget=widgets.Select(multiple=False),
        get_label='name'
    )
    submit = SubmitField('Send Application')


class ConfirmForm(FlaskForm):
    id = StringField('Application ID', validators=[DataRequired()])
    justification = TextAreaField('Give A Justification: ')
    accept = SubmitField('Accept')
    reject = SubmitField('Reject')
