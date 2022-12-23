from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from flask_wtf.file import FileAllowed, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User

class RegistrationForm(FlaskForm):
    # the green text in quotes is called "the Label"
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        # username=username.data storing the username data entered into username argument
        user = User.query.filter_by(username=username.data).first()
        # user anything other than none we get the error. basically checking if the username already exists in the database or not
        if user:
            raise ValidationError('Username already registered. Kindly choose a different one')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        # user anything other than none we get the error
        if user:
            raise ValidationError('Email already registered. Kindly register with a different one')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        # only perform validation(user already exists in database) check if the new username different from the old. username.data, the .data part takes you to the data submitted and since we are already inside the forms file we dont have to use forms.username.data. This ensures that the user does not get any error if he keeps the existing username(or email) and click update without this he would have gotten that error.
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already registered. Kindly choose a different one')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            # user anything other than none we get the error
            if user:
                raise ValidationError('Email already registered. Kindly register with a different one')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')
