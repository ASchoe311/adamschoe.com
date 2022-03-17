import flask
from dotenv import dotenv_values
from flask_mail import Mail
import pathlib
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, current_user
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_wtf import Form
from wtforms import StringField, EmailField, TextAreaField, PasswordField
from wtforms.validators import Length, Email, InputRequired, Optional, ValidationError
import hashlib

application = flask.Flask(__name__)

SITE_ROOT = pathlib.Path(__file__).resolve().parent

application.config.update(
    APPLICATION_ROOT='/',
    SECRET_KEY=bytes(dotenv_values('.env')['FLASK_SECRET_KEY'], 'utf-8'),
    SITE_ROOT=SITE_ROOT,
    IMAGES_FOLDER=SITE_ROOT/'static'/'images',
    PDF_FOLDER=SITE_ROOT/'static'/'pdfs',
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,
    IMG_UPLOAD_FOLDER=SITE_ROOT/'static'/'images',
    PDF_UPLOAD_FOLDER=SITE_ROOT/'static'/'pdfs',
    DATABASE_FILENAME=SITE_ROOT/'sql'/'db.sqlite3',
    MAIL_SERVER='email-smtp.us-east-2.amazonaws.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=dotenv_values('.env')['SES_USERNAME'],
    MAIL_PASSWORD=dotenv_values('.env')['SES_PASSWORD'],
    MAIL_DEBUG=False,
    SQLALCHEMY_DATABASE_URI='sqlite:////tmp/db.sqlite',
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

db = SQLAlchemy(application)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False, unique=True)

    def __repr__(self):
        return '<User %r>' % self.username


class Extra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False, unique=True)
    proj_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

    def __repr__(self):
        return '{' + f"\"text\": \"{self.text}\", \"url\": \"{self.url}\"" + '}'

class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lang = db.Column(db.String(25), nullable=False)
    proj_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

    def __repr__(self):
        return f"\"{self.lang}\""

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    github_url = db.Column(db.String(80), nullable=False)
    image = db.Column(db.String(25), nullable=False)
    is_wip = db.Column(db.Boolean, nullable=False)
    extras = db.relationship('Extra', backref='project', lazy=True)
    languages = db.relationship('Language', backref='project', lazy=True)

    def __repr__(self):
        return '{' + f"\"id\": {self.id}, \"title\": \"{self.title}\", \"description\": \"{self.description}\", \"github_url\": \"{self.github_url}\", \"image\": \"{self.image}\", \"languages\": {Language.query.filter_by(proj_id=self.id).all()}, \"is_wip\": {'true' if self.is_wip else 'false'}, \"extras\": {Extra.query.filter_by(proj_id=self.id).all()}" + '}'
        # return '<Post %r>' % self.title


def init_db():
    db.drop_all()
    db.create_all()
    
    adminUser = User(username="adamschoe", email="aschoe@umich.edu", password=dotenv_values('.env')['ADMIN_PASS_HASH'])
    db.session.add(adminUser)
    db.session.commit()

    # QUEUEBOT
    proj = Project(title="QueueBot", github_url="https://github.com/ASchoe311/RicksDoorQueue", image="queuebotimg.webp", is_wip=False, description="QueueBot is a chat bot that runs in the staff GroupMe chat of my work. Since I and a majority of my coworkers are students, we often need shifts picked up. With a few simple commands QueueBot can keep track of the shift pickup queue for each day to simplify this process.")
    extras = [
        Extra(proj_id=1, text="Live Queue Site", url="http://doorqueue.adamschoe.com")
    ]
    languages = [
        Language(proj_id=1, lang="JavaScript"),
        Language(proj_id=1, lang="HTML5")
    ]
    db.session.add(proj)
    for ext in extras:
        db.session.add(ext)
    for lang in languages:
        db.session.add(lang)
    db.session.commit()

    # EASYTUYA
    proj = Project(title="EasyTuya", github_url="https://github.com/ASchoe311/EasyTuya", image="tuyaimg.webp", is_wip=True, description="EasyTuya is a package containing nearly all needed functionality for interacting with your Tuya powered IOT devices through Python and Tuya's web API.")
    extras = [
        Extra(proj_id=2, text="PyPi Release", url="https://pypi.org/project/EasyTuya"),
        Extra(proj_id=2, text="Documentation", url="https://aschoe311.github.io/EasyTuya")
    ]
    languages = [
        Language(proj_id=2, lang="Python")
    ]
    db.session.add(proj)
    for ext in extras:
        db.session.add(ext)
    db.session.commit()
    for lang in languages:
        db.session.add(lang)
    db.session.commit()

class LoginForm(Form):
    login = StringField(validators=[InputRequired()])
    password = PasswordField(validators=[InputRequired()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise ValidationError('Invalid user')
        # print(self.password.data)
        # we're comparing the plaintext pw with the the hash from the db
        if not user.password == hashlib.sha256(bytes(str(self.password.data), 'utf-8')).hexdigest():
        # to compare plain text passwords use
        # if user.password != self.password.data:
            # print(user.password, hashlib.sha256(bytes(str(self.password.data), 'utf-8')).hexdigest())
            raise ValidationError('Invalid password')

    def get_user(self):
        return db.session.query(User).filter_by(username='adamschoe').first()

class EmailForm(Form):
    name = StringField('name', validators=[InputRequired(), Length(min=6)])
    email = EmailField('email', validators=[InputRequired(), Email()])
    subject = StringField('subject', validators=[InputRequired(), Length(min=2)])
    body = TextAreaField('body', validators=[InputRequired(), Length(min=10)])


class MyModelView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated
        
    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return flask.redirect(flask.url_for('login', next=flask.request.url))

class MyAdminIndexView(AdminIndexView):

    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            self._template_args['status'] = 0
        else:
            self._template_args['status'] = 1
        form = LoginForm(flask.request.form)
        self._template_args['form'] = form
        return super(MyAdminIndexView, self).index()

admin = Admin(application, index_view=MyAdminIndexView())
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Project, db.session))
admin.add_view(MyModelView(Language, db.session))
admin.add_view(MyModelView(Extra, db.session))


mail = Mail()
mail.init_app(application)


