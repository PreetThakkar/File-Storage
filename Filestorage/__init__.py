from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# Create upload directory
import os
path = os.getcwd()
try:
    os.mkdir(os.path.join(path, "upload"))
except FileExistsError:
    pass
upload = os.path.join(os.getcwd(), "upload")
print(upload)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'ABCD1234'
app.config['UPLOAD_FOLDER'] = upload
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
db.create_all()
from Filestorage import routes