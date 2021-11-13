from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms.fields import StringField, PasswordField, SubmitField, BooleanField, SelectField, DecimalField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from cunyzero.models import User


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
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)] )
    password = PasswordField('Password', validators=[DataRequired()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png']) ])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("That username is taken, Please choose a different one.")

class ApplicationForm(FlaskForm):
    application_type = SelectField('Application type', choices=[('1', 'Register as students'),
                                                                ('2', 'Register as instructor')], default=1)
    firstname = StringField('Firstname', validators=[DataRequired()])
    lastname = StringField('Lastname', validators=[DataRequired()])
    intro = StringField('Self-Description')
    GPA = DecimalField('GPA')
    submit = SubmitField('Send Application')
