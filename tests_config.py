import os

basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False

#db config
SQLITE_DATABASE_NAME = 'booknote.db'

TESTING = True
CSRF_ENABLED = False

SQLALCHEMY_DATABASE_URI = "sqlite://"

OPENID_PROVIDERS = [{
                     'name': 'Google',
                     'url': 'https://www.google.com/accounts/o8/id',
                     'img': 'images/google_openid.jpeg'
                     }, ]

MIN_AUTOCOMPLITE_LENGTH = 1

SECRET_KEY = 'very unique test sectret key 12345'
