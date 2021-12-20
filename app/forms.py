from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, FileField, DateField
from wtforms.validators import DataRequired, EqualTo, Length, Regexp


class UserLogin(Form):
    userName = StringField('Enter your username', validators=[DataRequired()])
    pwd = PasswordField('Enter your password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Submit')


class UserReg(Form):
    userName = StringField('Username', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])
    pwd = PasswordField('Password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    pwd2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')


class ChangePassword(Form):
    oldPassword = PasswordField('Old Password', validators=[DataRequired()])
    newPassword = PasswordField('New Password', validators=[DataRequired(), EqualTo('confirmPassword',
                                                                                    message='Passwords must match.')])
    passwordConfirm = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('submit')


class editUser(Form):
    userName = StringField('Enter your username')
    borrowBook = IntegerField('How many books did you borrow')
    criminalNumber = IntegerField('The number of you get out of line')


class searchBook(Form):
    searchResult = StringField('What you want to search', validators=[DataRequired()])


class editBook(Form):
    bookName = StringField('Enter book name')
    publishTime = DateField('Enter published time')
    publisher = StringField('Enter book publisher')
    author = StringField('Enter author of the book')
    type = StringField('Enter type of the book')
    description = StringField('Enter description')


class addBook(Form):
    bookImg = FileField('Input your bookImg', validators=[DataRequired()])
    authorImg = FileField('Input your authorImg', validators=[DataRequired()])
    bookName = StringField('Enter book name', validators=[DataRequired()])
    publishTime = DateField('Enter published time', validators=[DataRequired()])
    publisher = StringField('Enter book publisher', validators=[DataRequired()])
    author = StringField('Enter author of the book', validators=[DataRequired()])
    type = StringField('Enter type of the book', validators=[DataRequired()])
    description = StringField('Enter description', validators=[DataRequired()])
    bookCount = StringField('How many books do you want to add', validators=[DataRequired()])
