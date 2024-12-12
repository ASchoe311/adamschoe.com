import os
import flask
import hashlib
import subprocess
from dotenv import dotenv_values
from werkzeug.utils import secure_filename
from flask_mail import Message
from flask_admin import helpers
import json
from init import application, Project, mail, User, LoginForm, EmailForm, Skill, BlockedDomain, myinfo, db
# from flask_migrate import Migrate
from flask_login import (
    login_user,
    LoginManager,
    current_user,
    login_required,
    logout_user
)
from PIL import Image, ImageOps
import requests
from werkzeug.middleware.proxy_fix import ProxyFix
import re
import datetime
from math import floor

application.wsgi_app = ProxyFix(application.wsgi_app, x_for=1, x_host=1)

# @application.before_request
# def before_request():
#     if not flask.request.is_secure:
#         url = flask.request.url.replace('http://', 'https://', 1)
#         code = 301
#         return flask.redirect(url, code=code)

login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message_category = "info"
login_manager.init_app(application)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

num_projects = 0


def allowed_img_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg', 'gif', 'webp']

def allowed_res_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['pdf', 'html']

@application.route('/')
def show_index():
    context = {
        'projects': sorted(
            json.loads(str(Project.query.all())
        ), key=lambda x: datetime.datetime.strptime(x['lastupdate'][1:-1], '%Y-%m-%dT%H:%M:%SZ'), reverse=True),
        'skills': sorted(
            json.loads(str(Skill.query.all())
        ), key=lambda x: x['prio']),
        'bio': db.session.execute(db.select(User.bio).where(User.username == "adamschoe")).all()[0].bio,
        'page': 'index',
    }
    # print(context)
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
    context = {'myinfo': myinfo, 'page': 'contact', 'alert_success': None}
    form = EmailForm(flask.request.form)
    if flask.request.method == 'POST' and form.validate():
        POST_params={'secret': dotenv_values('.env')['RECAPTCHA_SECRET'], 'response': form.data['recaptcha_token'], 'remoteip': flask.request.remote_addr}
        recaptcha_resp = requests.post("https://www.google.com/recaptcha/api/siteverify", params=POST_params).json()
        # print(recaptcha_resp.json())
        block_list = str(BlockedDomain.query.all())
        if form.data['email'].split("@")[1] in block_list or recaptcha_resp['score'] < 0.7:
            context['alert_success'] = False
            return flask.render_template('contact.html',**context, form=form)
        emailBody = f"{form.data['name']} <{form.data['email']}> says:\n\n{form.data['body']}"
        msg = Message(form.data['subject'], recipients=['aschoe@umich.edu'], body=emailBody, sender=('contactform@adamschoe.com'))
        # flask.flash(msg)
        try:
            mail.send(msg)
            # pass
        except:
            context['alert_success'] = False
            return flask.render_template('contact.html',**context, form=form)
        context['alert_success'] = True
        form.name.data = form.email.data = form.subject.data = form.body.data = ""
    return flask.render_template('contact.html', **context, form=form)
        

@application.route('/resume')
def show_resume():
    # iFrameUrl = f"https://docs.google.com/viewer?url=your_url_to_pdf&embedded=true"
    # return flask.render_template('resume.html', resFile=myinfo['resume_file'], page='resume')
    # return flask.redirect(flask.url_for('show_pdf', pdf=myinfo['resume_file']))
    # return flask.send_from_directory(application.config["PDF_UPLOAD_FOLDER"], myinfo['resume_file'])
    return show_pdf(myinfo['resume_file'])

@application.route("/images/<image>", methods=["GET"])
def show_image(image):
    return flask.send_from_directory(str(application.config["IMG_UPLOAD_FOLDER"]), image)

@application.route("/pdfs/<pdf>", methods=["GET"])
def show_pdf(pdf):
    return flask.send_from_directory(str(application.config["PDF_UPLOAD_FOLDER"]), pdf)

# @application.route("/static/images/<svg>", methods=["GET"])
# def show_svg(svg):
#     return flask.send_from_directory(application.static_folder, 'images/' + svg)

@application.route("/uploadimg", methods=["POST"])
@login_required
def upload_img():
    imgFile = flask.request.files['image']
    filename = secure_filename(imgFile.filename)
    if allowed_img_file(filename):
        savePath = os.path.join(application.config['IMG_UPLOAD_FOLDER'], filename)
        imgFile.save(savePath)
        img = Image.open(imgFile)
        newPath = os.path.join(application.config['IMG_UPLOAD_FOLDER'], filename.split('.')[0] + '.webp')
        img.save(newPath, format='webp')
    return flask.redirect('/admin')

def get_size(image):
    maxHeight = 394
    ratio = maxHeight/image.height
    return (floor(image.width * ratio), 394)

def padding(img, expected_size):
    desired_size = expected_size
    delta_width = desired_size[0] - img.size[0]
    delta_height = desired_size[1] - img.size[1]
    pad_width = delta_width // 2
    pad_height = delta_height // 2
    padding = (pad_width, pad_height, delta_width - pad_width, delta_height - pad_height)
    return ImageOps.expand(img, padding)


def resize_with_padding(img, expected_size):
    img.thumbnail((expected_size[0], expected_size[1]))
    # print(img.size)
    delta_width = expected_size[0] - img.size[0]
    delta_height = expected_size[1] - img.size[1]
    pad_width = delta_width // 2
    pad_height = delta_height // 2
    padding = (pad_width, pad_height, delta_width - pad_width, delta_height - pad_height)
    return ImageOps.expand(img, padding)

# TODO: Fix this
@application.route("/uploadprojectimg", methods=["POST"])
@login_required
def upload_project_img():
    imgFile = flask.request.files['projectimage']
    filename = secure_filename(imgFile.filename)
    if allowed_img_file(filename):
        savePath = os.path.join(application.config['IMG_UPLOAD_FOLDER'], filename)
        imgFile.save(savePath)
        im = Image.open(savePath)
        resized_im = resize_with_padding(im, (700, 394))
        newPath = os.path.join(application.config['IMG_UPLOAD_FOLDER'], filename.split('.')[0] + '.webp')
        resized_im.save(newPath, format='webp')
    return flask.redirect('/admin')


@application.route("/changeresume", methods=["POST"])
@login_required
def upload_resume():
    resFile = flask.request.files['pdf']
    filename = secure_filename(resFile.filename)
    # print(filename)
    if allowed_res_file(filename):
        savePath = os.path.join(application.config['PDF_UPLOAD_FOLDER'], "Adam Schoenfeld - aschoe@umich.edu.pdf")
        resFile.save(savePath)
        myinfo['resume_file'] = "Adam Schoenfeld - aschoe@umich.edu.pdf"
    return flask.redirect('/admin')

@application.route("/robots.txt", methods=["GET"])
def give_robots():
    return flask.send_from_directory(application.static_folder, "robots.txt")

@application.route("/sitemap.xml", methods=["GET"])
def give_sitemap():
    return flask.send_from_directory(application.static_folder, "sitemap.xml")

@application.route("/staticimage/<image>", methods=["GET"])
def static_image(image):
    return flask.send_from_directory(application.static_folder, "images/" + image)

@application.route("/updatecommits", methods=["GET"])
@login_required
def update_commits():
    subprocess.call("../githubapi.sh", shell=True)
    return flask.redirect('/admin')

if __name__ == '__main__':
    # init_db()
    application.run(debug=False)