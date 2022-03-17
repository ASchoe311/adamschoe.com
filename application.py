import os
import flask
import hashlib
from dotenv import dotenv_values
from werkzeug.utils import secure_filename
from flask_mail import Message
from flask_admin import helpers
import json
from init import application, init_db, Project, mail, User, LoginForm, EmailForm
# from flask_migrate import Migrate
from flask_login import (
    login_user,
    LoginManager,
    current_user,
    login_required,
    logout_user
)

login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message_category = "info"
login_manager.init_app(application)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

num_projects = 0


myinfo = {
    'resume_file': 'res.pdf',
    'phone_num': '914-539-5828',
    'emails': ['aschoe@umich.edu', 'adamrschoenfeld311@gmail.com']
}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg', 'gif']

@application.route('/')
def show_index():
    context = {'projects': json.loads(str(Project.query.all())), 'page': 'index'}
    return flask.render_template('index.html', **context)

@application.route('/login', methods=['POST'])
def login():
    form = LoginForm(flask.request.form)
    if helpers.validate_form_on_submit(form):
        user = form.get_user()
        login_user(user)

    if current_user.is_authenticated:
        return flask.redirect('/admin')
    return flask.render_template_string("<h1 style=\"text-align: center;\">INVALID LOGIN</h1>")

@application.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return flask.redirect(flask.url_for('show_index'))

@application.route("/contact", methods=["GET", "POST"])
def show_contact_info():
    context = {'myinfo': myinfo, 'page': 'contact', 'alert_success': False}
    form = EmailForm(flask.request.form)
    if flask.request.method == 'POST' and form.validate():
        emailBody = f"{form.data['name']} <{form.data['email']}> says:\n\n{form.data['body']}"
        msg = Message(form.data['subject'], recipients=['aschoe@umich.edu'], body=emailBody, sender=('contactform@adamschoe.com'))
        # flask.flash(msg)
        mail.send(msg)
        context['alert_success'] = True
        form.name.data = form.email.data = form.subject.data = form.body.data = ""
    return flask.render_template('contact.html', **context, form=form)
        

@application.route('/resume')
def show_resume():
    # iFrameUrl = f"https://docs.google.com/viewer?url=your_url_to_pdf&embedded=true"
    return flask.render_template('resume.html', resFile=myinfo['resume_file'], page='resume')
    # return flask.redirect(flask.url_for('show_pdf', pdf='res.pdf'))

@application.route("/static/images/<image>", methods=["GET"])
def show_image(image):
    return flask.send_from_directory(application.static_folder, 'images/' + image)

@application.route("/static/pdfs/<pdf>", methods=["GET"])
def show_pdf(pdf):
    return flask.send_from_directory(application.static_folder, 'pdfs/' + pdf)

@application.route("/static/images/<svg>", methods=["GET"])
def show_svg(svg):
    return flask.send_from_directory(application.static_folder, 'images/' + svg)

@application.route("/updateresume" , methods=["GET", "POST"])
@login_required
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
    init_db()
    application.run(debug=False)