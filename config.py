"""Insta485 development configuration."""

import pathlib
from dotenv import dotenv_values

# Root of this application, useful if it doesn't occupy an entire domain
APPLICATION_ROOT = '/'

# Secret key for encrypting cookies
SECRET_KEY = bytes(dotenv_values('.env')['FLASK_SECRET_KEY'], 'utf-8')
# File Upload to var/uploads/
SITE_ROOT = pathlib.Path(__file__).resolve().parent
IMAGES_FOLDER = SITE_ROOT/'static'/'images'
PDF_FOLDER = SITE_ROOT/'static'/'pdfs'
ALLOWED_IMG_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
IMG_UPLOAD_FOLDER = SITE_ROOT/'static'/'images'
PDF_UPLOAD_FOLDER = SITE_ROOT/'static'/'pdfs'
# Database file is var/insta485.sqlite3
DATABASE_FILENAME = SITE_ROOT/'sql'/'db.sqlite3'

# MAIL_SERVER = 'smtp.sendgrid.net'
# MAIL_PORT = 25
# MAIL_USE_TLS = True
# MAIL_USERNAME = dotenv_values('.env')['SENDGRID_USERNAME']
# MAIL_PASSWORD = dotenv_values('.env')['SENDGRID_PASSWORD']


MAIL_SERVER = 'email-smtp.us-east-2.amazonaws.com'
MAIL_PORT = 25
MAIL_USE_TLS = True
MAIL_USERNAME = dotenv_values('.env')['SES_USERNAME']
MAIL_PASSWORD = dotenv_values('.env')['SES_PASSWORD']

MAIL_DEBUG = False