from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(200), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    bookCount = db.Column(db.Integer)
    criminalRecord = db.Column(db.Integer)
    firstBorrowBookId = db.Column(db.Integer)
    secondBorrowBookId = db.Column(db.Integer)
    thirdBorrowBookId = db.Column(db.Integer)

    def __repr__(self):
        return '<User %r>' % self.userName

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verity_password(self, password):
        return check_password_hash(self.password_hash, password)


class Admin(UserMixin, db.Model):
    __tablename__ = 'Admin'
    id = db.Column(db.Integer, primary_key=True)
    adminName = db.Column(db.String(200), index=True, unique=True)
    password_hash = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Admin %r>' % self.adminName

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verity_password(self, password):
        return check_password_hash(self.password_hash, password)


class Book(UserMixin, db.Model):
    __tablename__ = 'Book'
    id = db.Column(db.Integer, primary_key=True)
    bookName = db.Column(db.String(300), index=True)
    publishTime = db.Column(db.Date, nullable=True)
    publisher = db.Column(db.String(100), index=True)
    author = db.Column(db.String(100), index=True)
    type = db.Column(db.String(100), index=True)
    description = db.Column(db.String(500), nullable=False)
    bookNumber = db.Column(db.Integer)
    bookImg = db.Column(db.String(500))
    authorImg = db.Column(db.String(500))

    def __repr__(self):
        return '<Book %r>' % self.bookName
