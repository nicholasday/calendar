from flask import Flask, render_template, url_for, redirect, request, flash
from flask.ext.login import LoginManager, login_required, login_user, current_user, logout_user
from hashlib import sha1
import datetime
import calendar
from flask.ext.sqlalchemy import SQLAlchemy
app = Flask(__name__)

# use a database per day
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
app.secret_key = 'the power of habit'

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

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship("Category", backref=db.backref('tasks', lazy="dynamic"))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", backref=db.backref('tasks', lazy="dynamic"))
    date = db.Column(db.DateTime)
    description = db.Column(db.Text)

    def __init__(self, name, category, description, date, user):
        self.name = name
        self.category = category
        self.user = user
        self.description = description
        self.date = datetime.datetime.strptime(date, "%m/%d/%Y")

    def __repr__(self):
        return '<Task %r>' % self.name

@app.route('/')
@login_required
def main():
    categories = Category.query.filter_by(user=current_user).all()
    list_calendar = calendar.Calendar(calendar.SUNDAY).monthdayscalendar(2015, 8)
    new_list_calendar = []
    for week in list_calendar:
        new_week = []
        for day in week:
            new_week.append([day])
        new_list_calendar.append(new_week)
    
    for category in categories:
        for task in category.tasks:
            if task.date.month == datetime.datetime.now().month:
                for week in new_list_calendar:
                    for day in week:
                        if day[0] == task.date.day:
                           day.append([task.category.color, task.id, task.name]) 

    mobile_list = []
    for week in new_list_calendar:
        for day in week:
            if day[0] == datetime.datetime.now().day:
                mobile_list = week

    date = datetime.datetime.now()
    return render_template('index.html', date=date, categories=categories, calendar=new_list_calendar, current_user=current_user, mobile_list=mobile_list)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if (request.method == 'POST'
            and request.form['username']
            and request.form['password']
            and request.form['email']):

        user = db.session.query(User).filter_by(username=request.form['username']).first()
        if user is not None:
            return 'That username is already taken'
        else:
            user = User(
                username=request.form['username'],
                password=request.form['password'],
                email=request.form['email'],
            )
            default_category = Category(
                name='default',
                color='black',
                user=user
            )
            db.session.add(user)
            db.session.add(default_category)
            db.session.commit()

            login_user(user)
            return redirect(url_for('main'))

        login_user(user)
        return redirect(url_for('main'))
    return render_template('login.html', current_user=current_user)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if (request.method == 'POST'
            and request.form['username']
            and request.form['password']):

        user = db.session.query(User).filter_by(
            username=request.form['username'],
            password=sha1(request.form['password'].encode('utf-8')).hexdigest()).first()
        if user is None:
            flash("Woah there! You didn't type something in right")
            return redirect(url_for('main'))
        login_user(user)
        return redirect(url_for('main'))
    return render_template('login.html', current_user=current_user)

@app.route("/date/<date>")
@login_required
def create_task_date(date):
    if len(date) == 1:
        date = datetime.datetime.now().strftime('%m') + '/0' + date + '/' + str(datetime.datetime.now().year)
    else:
        date = datetime.datetime.now().strftime('%m') + '/' + date + '/' + str(datetime.datetime.now().year)
    categories = Category.query.filter_by(user=current_user).all()
    return render_template("task.html", date=date, categories=categories, current_user=current_user, task=None)

@app.route("/task/<task_id>/delete")
@login_required
def delete_task(task_id):
    if task_id is None:
        flash("No task selected to be deleted")
        return redirect(url_for('main'))
    task = Task.query.filter_by(id=task_id, user=current_user).first()
    if task is None:
        flash("No task with that name")
        return redirect(url_for('main'))
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('main'))

@app.route("/task/<task_id>", methods=['GET', 'POST'])
@app.route("/task", methods=["POST", "GET"])
@login_required
def view_task(task_id=None):
    if request.method == 'GET':
        task = Task.query.filter_by(id=task_id, user=current_user).first()
        categories = Category.query.filter_by(user=current_user).all()
        if task is not None:
            date = task.date.strftime('%m/%d/%Y')
        else:
            date = datetime.datetime.now().strftime('%m/%d/%Y')
        return render_template("task.html", task=task, categories=categories, current_user=current_user, date=date)
    elif request.method == 'POST' and task_id is not None:
        task = Task.query.filter_by(id=task_id, user=current_user).first()
        if task is None:
            flash("No task with that name")
            return redirect(url_for('main'))
        category = Category.query.filter_by(name=request.form['category'], user=current_user).first()
        task.name = request.form['name']
        task.category = category
        task.description = request.form['description']
        task.date = datetime.datetime.strptime(request.form['date'], "%m/%d/%Y")
        db.session.commit()
        return redirect(url_for('main'))
    if request.method == 'POST' and task_id is None:
        category = request.form['category']
        date = request.form['date']
        name = request.form['name']
        description = request.form['description']
        if not (category and date and name and description):
            flash("You didn't put in all of the values")
            return redirect(url_for('main'))
        category = Category.query.filter_by(name=request.form['category'], user=current_user).first()
        if category is None:
            flash("No category with that name")
            return redirect(url_for('main'))
        new_task = Task(name, category, description, date, current_user)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('main'))

@app.route("/category/<category_id>", methods=['GET', 'POST'])
@app.route("/category", methods=["POST", "GET"])
@login_required
def view_category(category_id=None):
    if request.method == 'GET':
        category = Category.query.filter_by(id=category_id, user=current_user).first()
        return render_template("category.html", category=category, current_user=current_user)
    elif request.method == 'POST' and category_id == None:
        category = request.form['name']
        color = request.form['color']
        if not (category and color):
            flash("You didn't put in all of the values")
            return redirect(url_for('main'))
        category_search = Category.query.filter_by(name=category, user=current_user).first()
        if category_search is not None:
            flash("You already created a category with that name")
            return redirect(url_for('main'))
        new_category = Category(category, color, current_user)
        db.session.add(new_category)
        db.session.commit()
        return redirect(url_for('main'))
    elif request.method == 'POST' and category_id is not None:
        category = Category.query.filter_by(id=category_id, user=current_user).first()
        if category is None:
            flash("No category with that name")
            return redirect(url_for('main'))
        category.name = request.form['name']
        category.color = request.form['color']
        db.session.commit()
        return redirect(url_for('main'))

@app.route("/category/<category_id>/delete")
@login_required
def delete_category(category_id):
    if category_id is None:
        flash("No category selected to be deleted")
        return redirect(url_for('main'))
    category = Category.query.filter_by(id=category_id, user=current_user).first()
    if category is None:
        flash("No category with that name")
        return redirect(url_for('main'))
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('main'))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
