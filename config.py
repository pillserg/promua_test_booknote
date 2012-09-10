import os

basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True

#db config
SQLITE_DATABASE_NAME = 'booknote.db'

SQLALCHEMY_DATABASE_URI = ''.join(['sqlite:///', os.path.join(basedir, SQLITE_DATABASE_NAME), ])
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

#Forms config
CSRF_ENABLED = True
SECRET_KEY = '\xe1B\xca\xdb\x91N\x13\xb9\xccd\x7fdU\xbb\x17|'

