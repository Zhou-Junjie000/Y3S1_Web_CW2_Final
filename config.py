import os

WTF_CSRF_ENABLED = True
SECRET_KEY = '1BCDEFGHIJKLMNOPQRSTUVWXYZ12345'

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_COMMIT_ON_TEARDOWN = True
SQLALCHEMY_ECHO = False
