import pathlib
import os
import flask
import hashlib
from dotenv import dotenv_values
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
import sqlite3

application = flask.Flask(__name__)
application.config.from_pyfile('config.py')
# print(application.config.get_namespace('MAIL_'))
# print(application.config.get_namespace('SITE_'))
# print(pathlib.Path(__file__).resolve().parent)

mail = Mail()
mail.init_app(application)

myinfo = {
    'resume_file': 'res.pdf',
    'phone_num': '914-539-5828',
    'emails': ['aschoe@umich.edu', 'adamrschoenfeld311@gmail.com'],
    'addr_ln1': '817 Arch St',
    'addr_ln2': 'Apartment 4',
    'city': 'Ann Arbor',
    'state': 'Michigan',
    'zip': 48104
}

def dict_factory(cursor, row):
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def get_db():
    """Open a new database connection.

    Flask docs:
    https://flask.palletsprojects.com/en/1.0.x/appcontext/#storing-data
    """
    if 'sqlite_db' not in flask.g:
        db_filename = application.config['DATABASE_FILENAME']
        flask.g.sqlite_db = sqlite3.connect(str(db_filename))
        flask.g.sqlite_db.row_factory = dict_factory

        # Foreign keys have to be enabled per-connection.  This is an sqlite3
        # backwards compatibility thing.
        flask.g.sqlite_db.execute("PRAGMA foreign_keys = ON")

    return flask.g.sqlite_db

@application.teardown_appcontext
def close_db(error):
    """Close the database at the end of a request.

    Flask docs:
    https://flask.palletsprojects.com/en/1.0.x/appcontext/#storing-data
    """
    assert error or not error  # Needed to avoid superfluous style error
    sqlite_db = flask.g.pop('sqlite_db', None)
    if sqlite_db is not None:
        sqlite_db.commit()
        sqlite_db.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in application.config.ALLOWED_IMG_EXTENSIONS

@application.route('/')
def show_index():
    connection = get_db()
    cur = connection.execute(
        "SELECT * FROM projects"
    )
    projects = cur.fetchall()
    projects = {str(proj['proj_id']): {key: proj[key] for key in proj.keys() if key != 'proj_id'} for proj in projects}
    projects_ctx = [projects[key] for key in sorted(projects, key=lambda proj: proj, reverse=True)]
    context = {'projects': projects_ctx, 'page': 'index'}
    return flask.render_template('index.html', **context)

@application.route("/contact", methods=["GET", "POST"])
def show_contact_info():
    # connection = get_db()
    # cur = connection.execute(
    #     'SELECT * FROM myinfo'
    # )
    # myinfo = cur.fetchone()
    context = {'myinfo': myinfo, 'page': 'contact', 'alert_success': False}
    if flask.request.method == 'POST':
        formData = {}
        formData['name'] = flask.request.form.get('name')
        formData['email'] = flask.request.form.get('email')
        formData['subject'] = flask.request.form.get('subject')
        formData['body'] = flask.request.form.get('body')
        # print(formData)
        emailBody = f"{formData['name']} <{formData['email']}> says:\n\n{formData['body']}"
        msg = Message(formData['subject'], recipients=['aschoe@umich.edu'], body=emailBody, sender=('contactform@adamschoe.com'))
        # print(msg)
        mail.send(msg)
        context['alert_success'] = True
    return flask.render_template('contact.html', **context)
        

@application.route('/resume')
def show_resume():
    # connection = get_db()
    # cur = connection.execute(
    #     'SELECT resume_file FROM myinfo'
    # )
    # resFile = cur.fetchone()['resume_file']
    # iFrameUrl = f"https://docs.google.com/viewer?url=your_url_to_pdf&embedded=true"
    # return flask.render_template('resume.html', resFile=myinfo['resume_file'], page='resume')
    return flask.redirect(flask.url_for('show_pdf', pdf='res.pdf'))

@application.route("/static/images/<image>", methods=["GET"])
def show_image(image):
    return flask.send_from_directory(application.static_folder, 'images/' + image)

@application.route("/static/pdfs/<pdf>", methods=["GET"])
def show_pdf(pdf):
    return flask.send_from_directory(application.static_folder, 'pdfs/' + pdf)

@application.route("/addproject", methods=["GET", "POST"])
def add_project():
    if flask.request.method == 'GET':
        return flask.render_template('addproject.html')
    passwordInput = flask.request.form.get('password')
    realPass = dotenv_values('.env')['ADMIN_PASS_HASH']
    # print(flask.request.files['image'].filename)
    m = hashlib.sha256()
    m.update(bytes(passwordInput, 'utf-8'))
    hashed = m.hexdigest()
    if hashed == realPass:
        formData = {}
        formData['title'] = flask.request.form.get('title')
        formData['description'] = flask.request.form.get('description')
        formData['url'] = flask.request.form.get('git_url')
        formData['language'] = flask.request.form.get('language')
        file = flask.request.files['image']
        formData['image'] = file.filename
        formData['is_wip'] = True if flask.request.form.get('is_wip') is not None else False
        connection = get_db()
        connection.execute(
            'INSERT INTO projects(title, github_url, image, description, language, is_wip)'
            'VALUES (?,?,?,?,?,?)', (formData['title'], formData['url'], formData['image'], formData['description'], formData['language'], formData['is_wip'],)
        )
        connection.commit()
        if allowed_file(formData['image']):
            filename = secure_filename(file.filename)
            file.save(os.path.join(application.config['IMG_UPLOAD_FOLDER'], filename))
            return flask.render_template('addsuccess.html', redirect_url=flask.url_for('show_index'), uploadtype='PROJECT')
        # return flask.render_template('formresponse.html', form=formData)
        flask.abort(403)
    else:
        return flask.render_template_string('<h1 style="text-align: center;">Sorry, this is for my personal use only! Nice try though!</h1>')
        # flask.abort(403)

@application.route("/updateresume" , methods=["GET", "POST"])
def change_resume():
    if flask.request.method == 'GET':
        return flask.render_template('changeresume.html')
    passwordInput = flask.request.form.get('password')
    realPass = dotenv_values('.env')['ADMIN_PASS_HASH']
    # print(flask.request.files['image'].filename)
    m = hashlib.sha256()
    m.update(bytes(passwordInput, 'utf-8'))
    hashed = m.hexdigest()
    if hashed == realPass:
        filename = flask.request.files['resfile'].filename
        if '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf':
            flask.request.files['resfile'].save(os.path.join(application.config['PDF_UPLOAD_FOLDER'], 'res.pdf'))
            # myinfo['resume_file'] = filename
            return flask.render_template('addsuccess.html', redirect_url=flask.url_for('show_resume'), uploadtype='RESUME')
        flask.abort(403)
    else:
        return flask.render_template_string('<h1 style="text-align: center;">Sorry, this is for my personal use only! Nice try though!</h1>')

if __name__ == '__main__':
    application.run(debug=False)