from flask import render_template, flash, redirect, session, url_for, request
from flask_login import login_user, LoginManager, logout_user, login_required
from app import app, db
from .models import User, Book, Admin
from .forms import UserReg, UserLogin, ChangePassword, editUser, searchBook, editBook, addBook
from datetime import timedelta
import os
from werkzeug.utils import secure_filename
import random
from datetime import datetime
import logging

login_manager = LoginManager(app)
login_manager.login_view = 'login'
app.send_file_max_age_default = timedelta(seconds=1)
login_manager.session_protection = "strong"
basedir = os.path.abspath(os.path.dirname(__file__))  # 这一句一定得加，我也不知道为什么
# 日志
logging.basicConfig(level=logging.DEBUG)
handler = logging.FileHandler('app.log', encoding='UTF-8')
logging_format = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
handler.setFormatter(logging_format)
app.logger.addHandler(handler)


def create_app(config_name):
    login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def loginPage():
    app.logger.info('info log')
    app.logger.warning('warning log')
    return render_template('loginBase.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    app.logger.info('info log')
    form = UserReg()
    flash('Errors="%s"' %
          form.errors)
    if request.method == 'POST':
        # username = form.userName.data
        username = request.form.get('username')
        if User.query.filter_by(userName=username).first():
            msg = "The username already exists, please try another one"
            return render_template('registration.html',
                                   title='registration',
                                   form=form,
                                   msg=msg)
        elif Admin.query.filter_by(adminName=username).first():
            msg = "The username already exists, please try another one"
            return render_template('registration.html',
                                   title='registration',
                                   form=form,
                                   msg=msg)
        # elif form.pwd.data == form.pwd2.data and not ('admin' in username):
        elif request.form.get("pwd") == request.form.get("pwd2") and 'admin' not in username:
            # user = User(userName=form.userName.data, pwd=form.pwd.data)
            user = User(userName=request.form.get('username'), password=request.form.get('pwd'))
            user.firstBorrowBookId = 0
            user.secondBorrowBookId = 0
            user.thirdBorrowBookId = 0
            user.bookCount = 0
            user.criminalRecord = 0
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        # elif form.pwd.data == form.pwd2.data and 'admin' in username:
        elif request.form.get("pwd") == request.form.get("pwd2") and 'admin' in username:
            # admin = Admin(adminName=form.userName.data, pwd=form.pwd.data)
            admin = Admin(adminName=request.form.get('username'), password=request.form.get("pwd"))
            db.session.add(admin)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            msg = "The confirm password is inconsistent"
            return render_template('registration.html',
                                   title='registration',
                                   form=form,
                                   msg=msg)
    else:
        return render_template('registration.html',
                               title='registration',
                               form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    app.logger.info('info log')
    form = UserLogin()
    flash('Errors="%s"' %
          form.errors)
    if request.method == 'POST':
        # username = form.userName.data
        # password = form.pwd.data
        username = request.form.get("username")
        password = request.form.get("pwd")
        if username != 'superadmin':
            if 'admin' not in username:
                user = User.query.filter_by(userName=username).first()
                if user is not None:
                    if user.verity_password(password):
                        login_user(user, form.remember_me.data)
                        session['username'] = username
                        return redirect(url_for('personalPage'))
                    else:
                        msg = "Password mistake"
                        return render_template('Login.html',
                                               form=form,
                                               msg=msg)
                else:
                    msg = "User name does not exist"
                    return render_template('Login.html',
                                           form=form,
                                           msg=msg)

            else:
                admin = Admin.query.filter_by(adminName=username).first()
                if admin is not None:
                    if admin.verity_password(password):
                        login_user(admin, form.remember_me.data)
                        session['adminname'] = username
                        return redirect(url_for('adminPage'))
                    else:
                        msg = "Password mistake"
                        return render_template('Login.html',
                                               form=form,
                                               msg=msg)
                else:
                    msg = "Admin name does not exist"
                    return render_template('Login.html',
                                           form=form,
                                           msg=msg)
        else:
            if password == 'superadmin':
                session['supadmin'] = username
                return redirect(url_for('superAdmin'))
            else:
                msg = "Password mistake"
                return render_template('Login.html',
                                       form=form,
                                       msg=msg)
    else:
        return render_template('Login.html',
                               form=form, )


@app.route('/logout')
@login_required
def logout():
    app.logger.info('info log')
    session.pop('username', None)
    logout_user()
    return redirect(url_for('login') or request.args.get('next'))


@app.route('/personalPage')
def personalPage():
    app.logger.info('info log')
    username = session['username']
    return render_template('userBasePase.html',
                           username=username)


@app.route('/personalProfile')
def personalProfile():
    app.logger.info('info log')
    username = session['username']
    user = User.query.filter_by(userName=username).first()
    if user.bookCount == None or user.criminalRecord == None:
        user.bookCount = 0
        user.criminalRecord = 0
    return render_template('personalProfile.html',
                           user=user,
                           username=username)


@app.route('/borrowBook')
def borrowBook():
    app.logger.info('info log')
    username = session['username']
    books = []
    user = User.query.filter_by(userName=username).first()
    bookIds = [user.firstBorrowBookId, user.secondBorrowBookId, user.thirdBorrowBookId]
    for id in bookIds:
        books.append(Book.query.filter_by(id=id).first())
    return render_template('borrowBook.html',
                           username=username,
                           books=books)


@app.route('/returnBook/<id>')
def returnBook(id):
    app.logger.info('info log')
    username = session['username']
    book = Book.query.filter_by(id=id).first()
    user = User.query.filter_by(userName=username).first()
    book.bookNumber += 1
    if user.firstBorrowBookId == int(id):
        user.firstBorrowBookId = 0
    elif user.secondBorrowBookId == int(id):
        user.secondBorrowBookId = 0
    elif user.thirdBorrowBookId == int(id):
        user.thirdBorrowBookId = 0
    user.bookCount -= 1
    return redirect(url_for('borrowBook'))


@app.route('/adminPage')
def adminPage():
    app.logger.info('info log')
    adminname = session['adminname']
    return render_template('adminBasePage.html',
                           adminname=adminname)


@app.route('/superAdmin')
def superAdmin():
    app.logger.info('info log')
    supadminname = session['supadmin']
    return render_template('superAdminBasePage.html',
                           supadminname=supadminname)


@app.route('/changePasswordForUser', methods=['GET', 'POST'])
def changePasswordForUser():
    app.logger.debug('info debug')
    form = ChangePassword()
    username = session['username']
    user = User.query.filter_by(userName=username).first()
    # if form.oldPassword.data == user.pwd:
    if request.method == 'POST':
        if user.verity_password(request.form.get("oldpass")):
            # if form.newPassword.data == form.passwordConfirm.data:
            if request.form.get("newpass") == request.form.get("conpass"):
                # user.pwd = form.newPassword.data
                user.password = request.form.get("newpass")
                db.session.commit()
                return redirect(url_for('personalPage'))
            else:
                msg = "The confirm password is inconsistent"
                return render_template('changePasswordForUser.html',
                                       form=form,
                                       username=username,
                                       msg=msg)
        # elif form.oldPassword.data != user.pwd and form.oldPassword.data:
        elif request.form.get("oldpass") != user.pwd and request.form.get("oldpass"):
            msg = "Old password incorrect"
            return render_template('changePasswordForUser.html',
                                   form=form,
                                   username=username,
                                   msg=msg)
    return render_template('changePasswordForUser.html',
                           form=form,
                           username=username)


@app.route('/changePasswordForAdmin', methods=['GET', 'POST'])
def changePasswordForAdmin():
    app.logger.debug('info debug')
    form = ChangePassword()
    adminname = session['adminname']
    admin = Admin.query.filter_by(adminName=adminname).first()
    if request.method == 'POST':
        if admin.verity_password(request.form.get('oldpass')):
            if request.form.get('newpass') == request.form.get('conpass'):
                admin.password = request.form.get('newpass')
                db.session.commit()
                return redirect(url_for('adminPage'))
            else:
                msg = "The confirm password is inconsistent"
                return render_template('changePasswordForAdmin.html',
                                       form=form,
                                       adminname=adminname,
                                       msg=msg)
        elif request.form.get('oldpass') != admin.pwd and request.form.get('oldpass'):
            msg = "Old password incorrect"
            return render_template('changePasswordForAdmin.html',
                                   form=form,
                                   adminname=adminname,
                                   msg=msg)
    return render_template('changePasswordForAdmin.html',
                           form=form,
                           adminname=adminname)


@app.route('/userListForAdmin')
def userListForAdmin():
    app.logger.info('info log')
    adminname = session['adminname']
    users = User.query.all()
    for user in users:
        if user.bookCount is None:
            user.bookCount = 0
    return render_template('userListForAdmin.html',
                           adminname=adminname,
                           users=users)


@app.route('/userListForSupAdmin')
def userListForSupAdmin():
    app.logger.info('info log')
    users = User.query.all()
    for user in users:
        if user.bookCount is None:
            user.bookCount = 0
    return render_template('userListForSupAdmin.html',
                           users=users,
                           supadminname='superadmin')


@app.route('/adminList')
def adminList():
    app.logger.info('info log')
    admins = Admin.query.all()
    return render_template('adminList.html',
                           admins=admins,
                           supadminname='superadmin')


@app.route('/deleteUserForAdmin/<id>')
def deleteUserForAdmin(id):
    app.logger.info('info log')
    user = User.query.filter_by(id=id).first()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('userListForAdmin'))


@app.route('/deleteUserForSupAdmin/<id>')
def deleteUserForSupAdmin(id):
    app.logger.info('info log')
    user = User.query.filter_by(id=id).first()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('userListForSupAdmin'))


@app.route('/deleteAdmin/<id>')
def deleteAdmin(id):
    app.logger.info('info log')
    admin = Admin.query.filter_by(id=id).first()
    db.session.delete(admin)
    db.session.commit()
    return redirect(url_for('adminList'))


@app.route('/adminEditUser/<id>', methods=['GET', 'POST'])
def adminEditUser(id):
    app.logger.info('info log')
    adminname = session['adminname']
    user = User.query.filter_by(id=id).first()
    form = editUser()
    usernameTemp = user.userName
    bookCountTemp = user.bookCount
    crimialTemp = user.criminalRecord
    if request.method == 'POST':
        if User.query.filter_by(userName=form.userName.data).first():
            msg = "This username has existed, please change another one."
            return render_template("adminEditUser.html",
                                   form=form,
                                   adminname=adminname,
                                   user=user,
                                   msg=msg)
        # user.userName = form.userName.data
        # user.bookCount = form.borrowBook.data
        # user.criminalRecord = form.criminalNumber.data
        user.userName = request.form.get('username')
        user.bookCount = request.form.get('borrowbook')
        user.criminalRecord = request.form.get('criminal')
        if user.userName is '':    user.userName = usernameTemp
        if user.bookCount is None:    user.bookCount = bookCountTemp
        if user.criminalRecord is None:    user.criminalRecord = crimialTemp

        db.session.commit()
        return redirect(url_for('userListForAdmin'))
    if user.bookCount is None or user.criminalRecord is None:
        user.bookCount = 0
        user.criminalRecord = 0
    return render_template('adminEditUser.html',
                           form=form,
                           adminname=adminname,
                           user=user)


@app.route('/supAdminEditUser/<id>', methods=['GET', 'POST'])
def supAdminEditUser(id):
    app.logger.info('info log')
    user = User.query.filter_by(id=id).first()
    form = editUser()
    usernameTemp = user.userName
    bookCountTemp = user.bookCount
    crimialTemp = user.criminalRecord
    if request.method == 'POST':
        if User.query.filter_by(userName=form.userName.data).first():
            msg = "This username has existed, please change another one."
            return render_template("superAdminEditUser.html",
                                   form=form,
                                   supadminname='superadmin',
                                   user=user,
                                   msg=msg)
        # user.userName = form.userName.data
        # user.bookCount = form.borrowBook.data
        # user.criminalRecord = form.criminalNumber.data
        user.userName = request.form.get('username')
        user.bookCount = request.form.get('borrowbook')
        user.criminalRecord = request.form.get('criminal')
        if user.userName is '':    user.userName = usernameTemp
        if user.bookCount is None:    user.bookCount = bookCountTemp
        if user.criminalRecord is None:    user.criminalRecord = crimialTemp
        if user.bookCount == 2: user.thirdBorrowBookId = 0
        if user.bookCount == 1:
            user.thirdBorrowBookId = 0
            user.secondBorrowBookId = 0
        if user.bookCount == 0:
            user.thirdBorrowBookId = 0
            user.secondBorrowBookId = 0
            user.firstBorrowBookId = 0

        db.session.commit()
        return redirect(url_for('userListForSupAdmin'))
    if user.bookCount is None or user.criminalRecord is None:
        user.bookCount = 0
        user.criminalRecord = 0
    return render_template('superAdminEditUser.html',
                           form=form,
                           supadminname='superadmin',
                           user=user)


@app.route('/bookRecommend', methods=['GET', 'POST'])
def bookRecommend():
    app.logger.info('info log')
    username = session['username']
    form = searchBook()
    if request.method == 'POST':
        # search = form.searchResult.data
        search = request.form.get('search')
        resultBook = Book.query.filter(Book.bookName.like('%' + search + '%')).all()
        resultAuthor = Book.query.filter(Book.author.like('%' + search + '%')).all()
        return render_template('searchReslutForUser.html',
                               resultBook=resultBook,
                               resultAuthor=resultAuthor,
                               form=form,
                               username=username)
    return render_template('bookRecommend.html',
                           username=username,
                           form=form)


@app.route('/bookListForAdmin')
def bookListForAdmin():
    app.logger.info('info log')
    adminname = session['adminname']
    books = Book.query.all()
    return render_template('adminViewBook.html',
                           adminname=adminname,
                           books=books)


@app.route('/bookListForSupAdmin')
def bookListForSupAdmin():
    app.logger.info('info log')
    books = Book.query.all()
    return render_template('superAdminViewBook.html',
                           supadminname='superadmin',
                           books=books)


@app.route('/adminDeleteBook/<id>')
def adminDeleteBook(id):
    app.logger.info('info log')
    book = Book.query.filter_by(id=id).first()
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('bookListForAdmin'))


@app.route('/supAdminDeleteBook/<id>')
def supAdminDeleteBook(id):
    app.logger.info('info log')
    book = Book.query.filter_by(id=id).first()
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('bookListForSupAdmin'))


@app.route('/adminEditBook/<id>', methods=['GET', 'POST'])
def adminEditBook(id):
    app.logger.debug('info log')
    adminname = session['adminname']
    book = Book.query.filter_by(id=id).first()
    form = editBook()
    bookNameTmp = book.bookName
    publishTimeTmp = book.publishTime
    publisherTmp = book.publisher
    authorTmp = book.author
    typeTmp = book.type
    bookNumTmp = book.bookNumber
    descriptionTmp = book.description
    if request.method == 'POST':
        # book.bookName = form.bookName.data
        # book.publishTime = form.publishTime.data
        # book.publisher = form.publisher.data
        # book.author = form.author.data
        # book.type = form.type.data
        # book.description = form.description.data
        book.bookName = request.form.get('bookname')
        book.publishTime = request.form.get('publishtime')
        book.publisher = request.form.get('publisher')
        book.author = request.form.get('author')
        book.type = request.form.get('type')
        book.bookNumber = request.form.get('number')
        book.description = request.form['des']

        if book.bookName == '':
            book.bookName = bookNameTmp
        if book.publishTime == '':
            book.publishTime = publishTimeTmp
        if book.publisher == '':
            book.publisher = publisherTmp
        if book.author == '':
            book.author = authorTmp
        if book.type == '':
            book.type = typeTmp
        if book.bookNumber == '':
            book.bookNumber = bookNumTmp
        if book.description == None:
            book.description = descriptionTmp
        db.session.commit()
        return redirect(url_for('bookListForAdmin'))
    return render_template('adminEditBook.html',
                           adminname=adminname,
                           form=form,
                           book=book)


@app.route('/supAdminEditBook/<id>', methods=['GET', 'POST'])
def supAdminEditBook(id):
    app.logger.debug('info log')
    book = Book.query.filter_by(id=id).first()
    form = editBook()
    bookNameTmp = book.bookName
    publishTimeTmp = book.publishTime
    publisherTmp = book.publisher
    authorTmp = book.author
    typeTmp = book.type
    bookNumTmp = book.bookNumber
    descriptionTmp = book.description
    if request.method == 'POST':
        book.bookName = request.form.get('bookname')
        book.publishTime = request.form.get('publishtime')
        book.publisher = request.form.get('publisher')
        book.author = request.form.get('author')
        book.type = request.form.get('type')
        book.bookNumber = request.form.get('number')
        book.description = request.form['des']

        if book.bookName == '':
            book.bookName = bookNameTmp
        if book.publishTime == '':
            book.publishTime = publishTimeTmp
        if book.publisher == '':
            book.publisher = publisherTmp
        if book.author == '':
            book.author = authorTmp
        if book.type == '':
            book.type = typeTmp
        if book.bookNumber == '':
            book.bookNumber = bookNumTmp
        if book.description == None:
            book.description = descriptionTmp
        db.session.commit()
        return redirect(url_for('bookListForSupAdmin'))
    return render_template('superAdminEditBook.html',
                           supadminname='superadmin',
                           form=form,
                           book=book)


@app.route('/adminAddBook', methods=['GET', 'POST'])
def adminAddBook():
    app.logger.warning('info warning')
    adminname = session['adminname']
    form = addBook()
    imgNumber = Book.query.count() + 1
    if request.method == 'POST':
        # 加书的图片
        bookFile = request.files['bookFile']
        bookFileSuffix = secure_filename(bookFile.filename).split('.')[-1]
        bookFilename = f"{imgNumber}_{random.randint(1, 99999)}.{bookFileSuffix}"
        bookFile.save(os.path.abspath(os.path.dirname(__file__)) + "/static/bookImg/" + bookFilename)
        # 作者的图片
        authorFile = request.files['authorFile']
        authorFileSuffix = secure_filename(authorFile.filename).split('.')[-1]
        authorFilename = f"{imgNumber}_{random.randint(1, 99999)}.{authorFileSuffix}"
        authorFile.save(os.path.abspath(os.path.dirname(__file__)) + "/static/authorImg/" + authorFilename)

        # bookName = form.bookName.data
        # publishTime = form.publishTime.data
        # publisher = form.publisher.data
        # author = form.author.data
        # type = form.type.data
        # bookNumber = form.bookCount.data
        # description = form.description.data
        bookName = request.form.get("bookname")
        publishTime = request.form.get("publishtime")
        publishTime = datetime.strptime(publishTime, "%Y-%m-%d").date()
        publisher = request.form.get("publisher")
        author = request.form.get("author")
        type = request.form.get("type")
        bookNumber = request.form.get("number")
        description = request.form['des']
        # 验证加入的书是否已经存在
        book = Book.query.filter_by(bookName=bookName).first()
        if book and book.author == author and book.publisher == publisher and book.publishTime == publishTime:
            book.bookNumber += 1
            db.session.commit()
            return redirect(url_for('bookListForAdmin'))
        newBook = Book(bookName=bookName, publishTime=publishTime, publisher=publisher, author=author, type=type,
                       description=description, bookNumber=bookNumber, bookImg=f"bookImg/{bookFilename}",
                       authorImg=f"authorImg/{authorFilename}")
        db.session.add(newBook)
        db.session.commit()
        return redirect(url_for('bookListForAdmin'))
    return render_template('adminAddBook.html',
                           adminname=adminname,
                           form=form)


@app.route('/supadminAddBook', methods=['GET', 'POST'])
def supadminAddBook():
    app.logger.warning('info warning')
    form = addBook()
    imgNumber = Book.query.count() + 1
    if request.method == 'POST':
        # 加书的图片
        bookFile = request.files['bookFile']
        bookFileSuffix = secure_filename(bookFile.filename).split('.')[-1]
        bookFilename = f"{imgNumber}_{random.randint(1, 99999)}.{bookFileSuffix}"
        bookFile.save(os.path.abspath(os.path.dirname(__file__)) + "/static/bookImg/" + bookFilename)
        # 作者的图片
        authorFile = request.files['authorFile']
        authorFileSuffix = secure_filename(authorFile.filename).split('.')[-1]
        authorFilename = f"{imgNumber}_{random.randint(1, 99999)}.{authorFileSuffix}"
        authorFile.save(os.path.abspath(os.path.dirname(__file__)) + "/static/authorImg/" + authorFilename)

        # bookName = form.bookName.data
        # publishTime = form.publishTime.data
        # publisher = form.publisher.data
        # author = form.author.data
        # type = form.type.data
        # bookNumber = form.bookCount.data
        # description = form.description.data
        bookName = request.form.get("bookname")
        publishTime = request.form.get("publishtime")
        publishTime = datetime.strptime(publishTime, "%Y-%m-%d").date()
        publisher = request.form.get("publisher")
        author = request.form.get("author")
        type = request.form.get("type")
        bookNumber = request.form.get("number")
        description = request.form['des']
        # 验证加入的书是否已经存在
        book = Book.query.filter_by(bookName=bookName).first()
        if book and book.author == author and book.publisher == publisher and book.publishTime == publishTime:
            book.bookNumber += 1
            db.session.commit()
            return redirect(url_for('bookListForAdmin'))
        newBook = Book(bookName=bookName, publishTime=publishTime, publisher=publisher, author=author, type=type,
                       description=description, bookNumber=bookNumber, bookImg=f"bookImg/{bookFilename}",
                       authorImg=f"authorImg/{authorFilename}")
        db.session.add(newBook)
        db.session.commit()
        return redirect(url_for('bookListForSupAdmin'))
    return render_template('superAdminAddBook.html',
                           supadminname='superadmin',
                           form=form)


@app.route('/allBookForUser')
def allBookForUser():
    app.logger.info('info log')
    username = session['username']
    books = Book.query.all()
    return render_template('allBook.html',
                           username=username,
                           books=books)


@app.route('/fictionBookForUser')
def fictionBookForUser():
    app.logger.info('info log')
    username = session['username']
    books = Book.query.filter_by(type='fiction').all()
    return render_template('fictionBook.html',
                           username=username,
                           books=books)


@app.route('/poemBookForUser')
def poemBookForUser():
    app.logger.info('info log')
    username = session['username']
    books = Book.query.filter_by(type='poem').all()
    return render_template('poemBook.html',
                           username=username,
                           books=books)


@app.route('/fairytailBookForUser')
def fairytailBookForUser():
    app.logger.info('info log')
    username = session['username']
    books = Book.query.filter_by(type='fairy tail').all()
    return render_template('fairyTailBook.html',
                           username=username,
                           books=books)


@app.route('/otherBookForUser')
def otherBookForUser():
    app.logger.info('info log')
    username = session['username']
    books = Book.query.filter(Book.type != 'poem', Book.type != 'fairy tail', Book.type != 'fiction').all()
    return render_template('fairyTailBook.html',
                           username=username,
                           books=books)


@app.route('/userBorrowBookInAllBook/<id>', methods=['GET', 'POST'])
def userBorrowBookInAllBook(id):
    app.logger.info('info log')
    username = session['username']
    user = User.query.filter_by(userName=username).first()
    book = Book.query.filter_by(id=id).first()
    books = Book.query.all()
    if user.bookCount >= 3:
        msg = "The number of books you borrowed has reached the upper limit."
        return render_template("allBook.html",
                               username=username,
                               msg=msg,
                               books=books)
    if book.bookNumber < 1:
        msg = "The book is temporarily unavailable"
        return render_template("allBook.html",
                               username=username,
                               msg=msg,
                               books=books)
    # 这里有一个大坑，就是数据类型的问题，python中不用自己定义数据类型，所以时常会出现这样的问题
    # 第一本书可以放，放在第一本书上
    if user.firstBorrowBookId == 0:
        user.firstBorrowBookId = int(id)
        user.bookCount += 1
        book.bookNumber -= 1
        db.session.commit()
        return redirect(url_for('allBookForUser'))
    # 第二本书可放
    elif user.firstBorrowBookId != 0 and user.secondBorrowBookId == 0:
        if int(id) != user.firstBorrowBookId:
            user.secondBorrowBookId = int(id)
            user.bookCount += 1
            book.bookNumber -= 1
            db.session.commit()
            return redirect(url_for('allBookForUser'))
        else:
            msg = "You have borrowed this book before"
            return render_template('allBook.html',
                                   username=username,
                                   books=books,
                                   msg=msg)
    # 第三本书可放
    elif user.firstBorrowBookId != 0 and user.secondBorrowBookId != 0 and user.thirdBorrowBookId == 0:
        if int(id) != user.firstBorrowBookId and int(id) != user.secondBorrowBookId:

            user.thirdBorrowBookId = int(id)
            user.bookCount += 1
            book.bookNumber -= 1
            db.session.commit()
            return redirect(url_for('allBookForUser'))
        else:
            msg = "You have borrowed this book before"
            return render_template('allBook.html',
                                   username=username,
                                   books=books,
                                   msg=msg)
    return render_template('allBook.html',
                           username=username,
                           books=books)


@app.route('/userBorrowBookInFictionBook/<id>', methods=['GET', 'POST'])
def userBorrowBookInFictionBook(id):
    app.logger.info('info log')
    username = session['username']
    user = User.query.filter_by(userName=username).first()
    book = Book.query.filter_by(id=id).first()
    books = Book.query.all()
    if user.bookCount >= 3:
        msg = "The number of books you borrowed has reached the upper limit."
        return render_template("allBook.html",
                               username=username,
                               msg=msg,
                               books=books)
    if book.bookNumber < 1:
        msg = "The book is temporarily unavailable"
        return render_template("allBook.html",
                               username=username,
                               msg=msg,
                               books=books)
    # 这里有一个大坑，就是数据类型的问题，python中不用自己定义数据类型，所以时常会出现这样的问题
    # 第一本书可以放，放在第一本书上
    if user.firstBorrowBookId == 0:
        user.firstBorrowBookId = int(id)
        user.bookCount += 1
        book.bookNumber -= 1
        db.session.commit()
        return redirect(url_for('allBookForUser'))
    # 第二本书可放
    elif user.firstBorrowBookId != 0 and user.secondBorrowBookId == 0:
        if int(id) != user.firstBorrowBookId:
            user.secondBorrowBookId = int(id)
            user.bookCount += 1
            book.bookNumber -= 1
            db.session.commit()
            return redirect(url_for('allBookForUser'))
        else:
            msg = "You have borrowed this book before"
            return render_template('allBook.html',
                                   username=username,
                                   books=books,
                                   msg=msg)
    # 第三本书可放
    elif user.firstBorrowBookId != 0 and user.secondBorrowBookId != 0 and user.thirdBorrowBookId == 0:
        if int(id) != user.firstBorrowBookId and int(id) != user.secondBorrowBookId:

            user.thirdBorrowBookId = int(id)
            user.bookCount += 1
            book.bookNumber -= 1
            db.session.commit()
            return redirect(url_for('allBookForUser'))
        else:
            msg = "You have borrowed this book before"
            return render_template('allBook.html',
                                   username=username,
                                   books=books,
                                   msg=msg)
    return render_template('allBook.html',
                           username=username,
                           books=books)


@app.route('/userBorrowBookInPoemBook/<id>', methods=['GET', 'POST'])
def userBorrowBookInPoemBook(id):
    app.logger.info('info log')
    username = session['username']
    user = User.query.filter_by(userName=username).first()
    book = Book.query.filter_by(id=id).first()
    books = Book.query.all()
    if user.bookCount >= 3:
        msg = "The number of books you borrowed has reached the upper limit."
        return render_template("allBook.html",
                               username=username,
                               msg=msg,
                               books=books)
    if book.bookNumber < 1:
        msg = "The book is temporarily unavailable"
        return render_template("allBook.html",
                               username=username,
                               msg=msg,
                               books=books)
    # 这里有一个大坑，就是数据类型的问题，python中不用自己定义数据类型，所以时常会出现这样的问题
    # 第一本书可以放，放在第一本书上
    if user.firstBorrowBookId == 0:
        user.firstBorrowBookId = int(id)
        user.bookCount += 1
        book.bookNumber -= 1
        db.session.commit()
        return redirect(url_for('allBookForUser'))
    # 第二本书可放
    elif user.firstBorrowBookId != 0 and user.secondBorrowBookId == 0:
        if int(id) != user.firstBorrowBookId:
            user.secondBorrowBookId = int(id)
            user.bookCount += 1
            book.bookNumber -= 1
            db.session.commit()
            return redirect(url_for('allBookForUser'))
        else:
            msg = "You have borrowed this book before"
            return render_template('allBook.html',
                                   username=username,
                                   books=books,
                                   msg=msg)
    # 第三本书可放
    elif user.firstBorrowBookId != 0 and user.secondBorrowBookId != 0 and user.thirdBorrowBookId == 0:
        if int(id) != user.firstBorrowBookId and int(id) != user.secondBorrowBookId:

            user.thirdBorrowBookId = int(id)
            user.bookCount += 1
            book.bookNumber -= 1
            db.session.commit()
            return redirect(url_for('allBookForUser'))
        else:
            msg = "You have borrowed this book before"
            return render_template('allBook.html',
                                   username=username,
                                   books=books,
                                   msg=msg)
    return render_template('allBook.html',
                           username=username,
                           books=books)


@app.route('/userBorrowBookInFairyTailBook/<id>', methods=['GET', 'POST'])
def userBorrowBookInFairyTailBook(id):
    app.logger.info('info log')
    username = session['username']
    user = User.query.filter_by(userName=username).first()
    book = Book.query.filter_by(id=id).first()
    books = Book.query.all()
    if user.bookCount >= 3:
        msg = "The number of books you borrowed has reached the upper limit."
        return render_template("allBook.html",
                               username=username,
                               msg=msg,
                               books=books)
    if book.bookNumber < 1:
        msg = "The book is temporarily unavailable"
        return render_template("allBook.html",
                               username=username,
                               msg=msg,
                               books=books)
    # 这里有一个大坑，就是数据类型的问题，python中不用自己定义数据类型，所以时常会出现这样的问题
    # 第一本书可以放，放在第一本书上
    if user.firstBorrowBookId == 0:
        user.firstBorrowBookId = int(id)
        user.bookCount += 1
        book.bookNumber -= 1
        db.session.commit()
        return redirect(url_for('allBookForUser'))
    # 第二本书可放
    elif user.firstBorrowBookId != 0 and user.secondBorrowBookId == 0:
        if int(id) != user.firstBorrowBookId:
            user.secondBorrowBookId = int(id)
            user.bookCount += 1
            book.bookNumber -= 1
            db.session.commit()
            return redirect(url_for('allBookForUser'))
        else:
            msg = "You have borrowed this book before"
            return render_template('allBook.html',
                                   username=username,
                                   books=books,
                                   msg=msg)
    # 第三本书可放
    elif user.firstBorrowBookId != 0 and user.secondBorrowBookId != 0 and user.thirdBorrowBookId == 0:
        if int(id) != user.firstBorrowBookId and int(id) != user.secondBorrowBookId:

            user.thirdBorrowBookId = int(id)
            user.bookCount += 1
            book.bookNumber -= 1
            db.session.commit()
            return redirect(url_for('allBookForUser'))
        else:
            msg = "You have borrowed this book before"
            return render_template('allBook.html',
                                   username=username,
                                   books=books,
                                   msg=msg)
    return render_template('allBook.html',
                           username=username,
                           books=books)


@app.route('/userBorrowBookInOtherBook/<id>', methods=['GET', 'POST'])
def userBorrowBookInOtherBook(id):
    app.logger.info('info log')
    username = session['username']
    user = User.query.filter_by(userName=username).first()
    book = Book.query.filter_by(id=id).first()
    books = Book.query.all()
    if user.bookCount >= 3:
        msg = "The number of books you borrowed has reached the upper limit."
        return render_template("allBook.html",
                               username=username,
                               msg=msg,
                               books=books)
    if book.bookNumber < 1:
        msg = "The book is temporarily unavailable"
        return render_template("allBook.html",
                               username=username,
                               msg=msg,
                               books=books)
    # 这里有一个大坑，就是数据类型的问题，python中不用自己定义数据类型，所以时常会出现这样的问题
    # 第一本书可以放，放在第一本书上
    if user.firstBorrowBookId == 0:
        user.firstBorrowBookId = int(id)
        user.bookCount += 1
        book.bookNumber -= 1
        db.session.commit()
        return redirect(url_for('allBookForUser'))
    # 第二本书可放
    elif user.firstBorrowBookId != 0 and user.secondBorrowBookId == 0:
        if int(id) != user.firstBorrowBookId:
            user.secondBorrowBookId = int(id)
            user.bookCount += 1
            book.bookNumber -= 1
            db.session.commit()
            return redirect(url_for('allBookForUser'))
        else:
            msg = "You have borrowed this book before"
            return render_template('allBook.html',
                                   username=username,
                                   books=books,
                                   msg=msg)
    # 第三本书可放
    elif user.firstBorrowBookId != 0 and user.secondBorrowBookId != 0 and user.thirdBorrowBookId == 0:
        if int(id) != user.firstBorrowBookId and int(id) != user.secondBorrowBookId:

            user.thirdBorrowBookId = int(id)
            user.bookCount += 1
            book.bookNumber -= 1
            db.session.commit()
            return redirect(url_for('allBookForUser'))
        else:
            msg = "You have borrowed this book before"
            return render_template('allBook.html',
                                   username=username,
                                   books=books,
                                   msg=msg)
    return render_template('allBook.html',
                           username=username,
                           books=books)


@app.route('/userBorrowBookInDetailPage/<id>', methods=['GET', 'POST'])
def userBorrowBookInDetailPage(id):
    app.logger.info('info log')
    username = session['username']
    user = User.query.filter_by(userName=username).first()
    book = Book.query.filter_by(id=id).first()
    books = Book.query.all()
    if user.bookCount >= 3:
        msg = "The number of books you borrowed has reached the upper limit."
        return render_template("bookDetail.html",
                               username=username,
                               msg=msg,
                               books=books,
                               book=book)
    if book.bookNumber < 1:
        msg = "The book is temporarily unavailable"
        return render_template("bookDetail.html",
                               username=username,
                               msg=msg,
                               books=books,
                               book=book)
    # 这里有一个大坑，就是数据类型的问题，python中不用自己定义数据类型，所以时常会出现这样的问题
    # 第一本书可以放，放在第一本书上
    if user.firstBorrowBookId == 0:
        user.firstBorrowBookId = int(id)
        user.bookCount += 1
        book.bookNumber -= 1
        db.session.commit()
        return redirect(url_for('allBookForUser'))
    # 第二本书可放
    elif user.firstBorrowBookId != 0 and user.secondBorrowBookId == 0:
        if int(id) != user.firstBorrowBookId:
            user.secondBorrowBookId = int(id)
            user.bookCount += 1
            book.bookNumber -= 1
            db.session.commit()
            return redirect(url_for('allBookForUser'))
        else:
            msg = "You have borrowed this book before"
            return render_template('bookDetail.html',
                                   username=username,
                                   books=books,
                                   msg=msg,
                                   book=book)
    # 第三本书可放
    elif user.firstBorrowBookId != 0 and user.secondBorrowBookId != 0 and user.thirdBorrowBookId == 0:
        if int(id) != user.firstBorrowBookId and int(id) != user.secondBorrowBookId:

            user.thirdBorrowBookId = int(id)
            user.bookCount += 1
            book.bookNumber -= 1
            db.session.commit()
            return redirect(url_for('allBookForUser'))
        else:
            msg = "You have borrowed this book before"
            return render_template('bookDetail.html',
                                   username=username,
                                   books=books,
                                   msg=msg,
                                   book=book)
    return render_template('allBook.html',
                           username=username,
                           books=books,
                           book=book)


@app.route('/searchBookForAdmin', methods=['GET', 'POST'])
def searchBookForAdmin():
    app.logger.debug('info debug')
    adminname = session['adminname']
    form = searchBook()
    if request.method == 'POST':
        # search = form.searchResult.data
        search = request.form.get('search')
        resultBook = Book.query.filter(Book.bookName.like('%' + search + '%')).all()
        resultAuthor = Book.query.filter(Book.author.like('%' + search + '%')).all()
        return render_template('searchResultForAdmin.html',
                               adminname=adminname,
                               resultBook=resultBook,
                               resultAuthor=resultAuthor,
                               form=form)
    return render_template('searchBaseForAdmin.html',
                           adminname=adminname,
                           form=form)


@app.route('/searchBookForSupAdmin', methods=['GET', 'POST'])
def searchBookForSupAdmin():
    app.logger.debug('info debug')
    form = searchBook()
    if request.method == 'POST':
        # search = form.searchResult.data
        search = request.form.get('search')
        resultBook = Book.query.filter(Book.bookName.like('%' + search + '%')).all()
        resultAuthor = Book.query.filter(Book.author.like('%' + search + '%')).all()
        return render_template('searchResultForSupAdmin.html',
                               supadminname='superadmin',
                               resultBook=resultBook,
                               resultAuthor=resultAuthor,
                               form=form)
    return render_template('searchBaseForSupAdmin.html',
                           supadminname='superadmin',
                           form=form)


@app.route('/searchBookForUser', methods=['GET', 'POST'])
def searchBookForUser():
    app.logger.debug('info debug')
    username = session['username']
    form = searchBook()
    if request.method == 'POST':
        # search = form.searchResult.data
        search = request.form.get('search')
        resultBook = Book.query.filter(Book.bookName.like('%' + search + '%')).all()
        resultAuthor = Book.query.filter(Book.author.like('%' + search + '%')).all()
        return render_template('searchReslutForUser.html',
                               resultBook=resultBook,
                               resultAuthor=resultAuthor,
                               form=form,
                               username=username)
    return render_template('searchBaseForUser.html',
                           username=username,
                           form=form)


@app.route('/bookDetail/<id>')
def bookDetail(id):
    app.logger.info('info log')
    username = session['username']
    book = Book.query.filter_by(id=id).first()
    return render_template('bookDetail.html',
                           book=book,
                           username=username)
