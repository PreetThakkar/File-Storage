from datetime import datetime
from Filestorage import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    file = db.relationship('File', backref='owner', lazy=True)

    def __repr__(self):
        return f"User({self.id}, {self.username}, {self.email})"

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"File({self.id}, {self.title}, {self.date})"