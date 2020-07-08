from app import app
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField,SubmitField,FloatField, BooleanField, PasswordField,RadioField, IntegerField,TextAreaField
from wtforms.validators import DataRequired, Length,Email,EqualTo

class RegistrationForm(FlaskForm):
    username =StringField('Username')
    firstname =StringField('Firstname')
    lastname =StringField('Lastname')
    email = StringField('Email')
    password = PasswordField('Password')
    confirm_password = PasswordField('Confirm Password')
    submit = SubmitField('Sign up')

class LoginForm(FlaskForm):
    username =StringField('Username')
    password = PasswordField('Password')
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ForgotForm(FlaskForm):    
    email = StringField('Email')
    password = PasswordField('Password')
    confirm_password = PasswordField('Confirm Password')
    submit = SubmitField('submit')
    
class UpdateAccountForm(FlaskForm):
    age =  IntegerField('Age')
    gender = RadioField('Gender', choices=[('Male','Male'),('Female','Female'),('Bisexual','Other')])
    sexualPreference = RadioField('SexualPreference',choices=[('Male','Male'),('Female','Female'),('Bisexual','Bisexual')])
    bio = TextAreaField('Biography')
    interest = StringField('Interest')
    picture = FileField('Upload picture')
    submit = SubmitField('Update')

class UploadsForm(FlaskForm):
    username =StringField('Username')
    firstname = StringField('Firstname')
    lastname = StringField("Lastname")
    email = StringField('Email')
    age =  IntegerField('Age')
    gender = RadioField('Gender', choices=[('Male','Male'),('Female','Female'),('Bisexual','Other')])
    sexualPreference = RadioField('SexualPreference',choices=[('Male','Male'),('Female','Female'),('Bisexual','Bisexual')])
    bio = TextAreaField('Biography')
    interest = StringField('Interest')
    city = StringField('New City')
    picture = FileField('Upload picture')
    submit = SubmitField('Update')


class PostForm(FlaskForm):
    title = StringField('Title',validators=[DataRequired(),])
    content = TextAreaField('Content',validators=[DataRequired()])
    submit = SubmitField('Post')

class MessageForm(FlaskForm):
    username = StringField('Username')
    content = TextAreaField('Content',validators=[DataRequired()])
    submit = SubmitField('send')