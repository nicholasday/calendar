from app import db, login_manager
from flask import url_for
from hashlib import sha1
import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    timestamp = db.Column(db.DateTime)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = sha1(password.encode('utf-8')).hexdigest()
        self.timestamp = datetime.datetime.utcnow()

    def __repr__(self):
        return '<User %r>' % self.username

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return str(self.id)
        except AttributeError:
            raise NotImplementedError('No `id` attribute - override `get_id`')

    @property
    def url(self):
        return url_for('userresource', id=self.id)

@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    color = db.Column(db.String(80))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", backref=db.backref('categories', lazy="dynamic"))

    def __init__(self, name, color, user):
        self.name = name
        self.color = color
        self.user = user

    def __repr__(self):
        return '<Category %r>' % self.name

    @property
    def url(self):
        return url_for('category', id=self.id)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship("Category", backref=db.backref('tasks', lazy="dynamic"))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", backref=db.backref('tasks', lazy="dynamic"))
    date = db.Column(db.DateTime)
    completed = db.Column(db.Boolean)
    description = db.Column(db.Text)

    def __init__(self, name, category, description, date, user):
        self.name = name
        self.category = category
        self.user = user
        self.description = description
        self.date = datetime.datetime.strptime(date, "%m/%d/%Y")
        self.completed = False

    def __repr__(self):
        return '<Task %r>' % self.name

    @property
    def url(self):
        return url_for('task', user_id=self.id)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship("Category", backref=db.backref('notes', lazy="dynamic"))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", backref=db.backref('notes', lazy="dynamic"))
    date = db.Column(db.DateTime)
    content = db.Column(db.Text)

    def __init__(self, name, category, content, user):
        self.name = name
        self.category = category
        self.user = user
        self.content = content
        self.date = datetime.datetime.now()

    def __repr__(self):
        return '<Note %r>' % self.name

    @property
    def url(self):
        return url_for('note', user_id=self.id)

class Due_date(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship("Category", backref=db.backref('due_dates', lazy="dynamic"))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", backref=db.backref('due_dates', lazy="dynamic"))
    date = db.Column(db.DateTime)
    description = db.Column(db.Text)

    def __init__(self, name, category, description, date, user):
        self.name = name
        self.category = category
        self.user = user
        self.description = description
        self.date = datetime.datetime.strptime(date, "%m/%d/%Y")

    def __repr__(self):
        return '<Due_date %r>' % self.name

    @property
    def url(self):
        return url_for('due_date', user_id=self.id)
