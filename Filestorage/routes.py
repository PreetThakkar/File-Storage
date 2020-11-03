from flask import render_template, url_for, redirect, flash, request, send_from_directory
from Filestorage.forms import RegistrationForm, LoginForm, UploadForm
from Filestorage import app, db, bcrypt
from werkzeug.utils import secure_filename
import os
from Filestorage.models import User, File
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, current_user, logout_user, login_required
from hashlib import md5

@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
@login_required
def home():
    if current_user.is_authenticated:
        files = {}
        folder = os.path.join(app.config["UPLOAD_FOLDER"], current_user.username)
        for item in os.listdir(folder):
            files[item] = os.path.join(folder, item)
        return render_template('home.html', title="Home", files=files)
    else:
        return render_template('home.html', title="Home")

@app.route('/home/<filename>')
def uploaded_file_view(filename):
    path = os.path.join(app.config['UPLOAD_FOLDER'], current_user.username)
    return send_from_directory(path, filename, as_attachment=False)

@app.route('/home/download/<filename>')
def uploaded_file_download(filename):
    path = os.path.join(app.config['UPLOAD_FOLDER'], current_user.username)
    return send_from_directory(path, filename, as_attachment=True)

@app.route('/home/delete/<filename>')
def uploaded_file_delete(filename):
    folder = os.path.join(app.config['UPLOAD_FOLDER'], current_user.username)
    file = os.path.join(folder, filename)
    db_file = File.query.filter_by(title=filename, user_id=current_user.id).first()
    db.session.delete(db_file)
    db.session.commit()
    os.remove(file)
    return redirect(url_for('home'))

@app.route('/uploader', methods=['GET', 'POST'])
def upload():
    if request.method=='POST':
        f = request.files['file']
        filename = secure_filename(f.filename)
        print(filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], current_user.username)
        hash_md5 = md5()
        try:
            os.mkdir(os.path.join(app.config["UPLOAD_FOLDER"], "temp"))
        except:
            pass
        temp_folder = os.path.join(app.config["UPLOAD_FOLDER"], "temp")
        f.save(os.path.join(temp_folder, filename))
        with open(os.path.join(temp_folder, filename), 'rb') as fi:
            for chunk in iter(lambda: fi.read(4096), b""):
                hash_md5.update(chunk)
        file = File.query.filter_by(content=hash_md5.hexdigest(), user_id=current_user.id).first()
        if file:
            flash(f'File Already exists', 'warning')
        else:
            ids = max([x.id for x in File.query.all()]) + 1
            os.rename(os.path.join(temp_folder, filename), os.path.join(path, filename))
            file = File(id=ids, title=filename, content=hash_md5.hexdigest(), user_id=current_user.id)
            db.session.add(file)
            db.session.commit()
            flash(f'Uploaded', 'success')
        return redirect(url_for('home'))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=password, email=form.email.data)
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            if User.query.filter_by(username=form.username.data):
                flash(f'Account for {form.username.data} already exists.', 'danger')
            elif User.query.filter_by(email=form.email.data):
                flash(f'Account for {form.email.data} already exists.', 'danger')
            return redirect(url_for("login"))
        flash(f'Account Created for {form.username.data} successfully', 'success')
        return redirect(url_for("login"))
    return render_template('register.html', title="Register", form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, form.remember.data)
            # flash(f'Welcome {form.email.data}', 'success')
            try:
                os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'], current_user.username))
                # os.mknod("Hello.txt")
                ids = max([x.id for x in File.query.all()]) + 1
                file = File(id=ids, title="Hello.txt", content=".", user_id=current_user.id)
                db.session.add(file)
                db.session.commit()
            except FileExistsError:
                pass
            return redirect(url_for("home"))
        flash(f'Check email or password', 'danger')
    return render_template('login.html', title="Login", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')
