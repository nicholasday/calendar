from flask import Flask, render_template, url_for, redirect, request, flash, jsonify
from flask.ext.login import LoginManager, login_required, login_user, current_user, logout_user
from flask.ext.sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import datetime
import random
import calendar
ma = Marshmallow()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'frontend.login'

#def create_app():
app = Flask(__name__)
#api = Api(app)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../test.db'
login_manager.init_app(app)
ma.init_app(app)
app.secret_key = 'the power of habit'
from app.backend import backend
from app.frontend import frontend
app.register_blueprint(backend)
app.register_blueprint(frontend)
#db.create_all()

#return app
from app import schemas

