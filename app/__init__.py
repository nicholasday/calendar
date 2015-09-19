from flask import Flask, render_template, url_for, redirect, request, flash, jsonify
from flask.ext.login import LoginManager, login_required, login_user, current_user, logout_user
from flask.ext.sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import datetime
import random
import calendar
from flask_admin import Admin, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
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

class MyModelView(ModelView):

    def is_accessible(self):
        if current_user.is_authenticated() and (current_user.username == 'nick'):
            return True
        else:
            return False

class MyAdminIndexView(AdminIndexView):

    @expose('/')
    def index(self):
        if not current_user.is_authenticated():
            return redirect(url_for('frontend.login'))
        if current_user.username == "nick":
            return super(MyAdminIndexView, self).index()
        else:
            return redirect(url_for('frontend.main'))

admin = Admin(app, name='Admin', index_view=MyAdminIndexView(), template_mode='bootstrap3')
from app.models import User, Note, Task, Due_date
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Note, db.session))
admin.add_view(MyModelView(Task, db.session))
admin.add_view(MyModelView(Due_date, db.session))
from app.backend import backend
from app.frontend import frontend
app.register_blueprint(backend)
app.register_blueprint(frontend)
#db.create_all()

#return app
from app import schemas

