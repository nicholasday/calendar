from flask import Flask, render_template, url_for, redirect, request, flash
from flask.ext.login import LoginManager, login_required, login_user, current_user, logout_user
from hashlib import sha1
import datetime
import random
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

@app.route('/date/<int:month>')
@app.route('/date/<int:month>/<int:week_number>')
@app.route('/date/<int:month>/<int:week_number>/<int:year>')
@app.route('/user/<user_id>')
@app.route('/')
def main(user_id=None, month=None, week_number=None, year=None):
    if user_id and current_user.username == 'nick':
        logged_in_user = User.query.filter_by(id=user_id).first()
    else:
        if current_user.is_authenticated():
            logged_in_user = current_user
        else:
            logged_in_user = User.query.filter_by(username='nick').first()
    categories = Category.query.filter_by(user=logged_in_user).all()

    if month == None:
        month = datetime.datetime.now().month

    if year == None:
        year = datetime.datetime.now().year

    list_calendar = calendar.Calendar(calendar.SUNDAY).monthdayscalendar(year, month)
    new_list_calendar = []
    for week in list_calendar:
        new_week = []
        for day in week:
            new_week.append([day])
        new_list_calendar.append(new_week)

    for category in categories:
        for due_date in category.due_dates:
            if due_date.date.month == month:
                for week in new_list_calendar:
                    for day in week:
                        if day[0] == due_date.date.day and month == due_date.date.month and year == due_date.date.year:
                           day.append([due_date.category.color, due_date.id, 'due_date', due_date.name]) 
    
    for category in categories:
        for task in category.tasks:
            if task.date.month == month:
                for week in new_list_calendar:
                    for day in week:
                        if day[0] == task.date.day and month == task.date.month and year == task.date.year:
                           day.append([task.category.color, task.id, 'task', task.completed, task.name]) 

    date = datetime.datetime.now()

    if week_number is None:
        week_number = 0
        for index, week in enumerate(new_list_calendar, start=0):
            for day in week:
                if day[0] == date.day:
                    week_number = index

    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    date = datetime.datetime.now()
    return render_template('index.html', days=days, week_number=week_number, month=calendar.month_name[month], month_number=month, year=year, date=date, categories=categories, calendar=new_list_calendar, logged_in_user=logged_in_user, current_user=current_user)

@app.route('/users')
@login_required
def list_users():
    if current_user.username == 'nick':
        users = User.query.all()
        return render_template("users.html", users=users)
    else:
        return redirect(url_for('main'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if (request.method == 'POST'
            and request.form['username']
            and request.form['password']
            and request.form['email']):

        user = db.session.query(User).filter_by(username=request.form['username']).first()
        if user is not None:
            flash('That username is already taken')
            return redirect(url_for('main'))
        else:
            user = User(
                username=request.form['username'],
                password=request.form['password'],
                email=request.form['email'],
            )
            default_category = Category(
                name='default',
                color='#000000',
                user=user
            )
            db.session.add(user)
            db.session.add(default_category)
            db.session.commit()

            login_user(user)
            flash("Click on a calendar box to add a task/due date. Due dates are highlighted in the category color. Add categories to change the task text color and the due date highlighted color. Click on a task/due date/category to edit/delete it. You can strikethrough on tasks by clicking on it and checking work completed. If you look at this website on mobile, it shows you the previous day and 6 days after, not the whole calendar.")
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

@app.route("/note/<note_id>/delete")
@login_required
def delete_note(note_id):
    if note_id is None:
        flash("No note selected to be deleted")
        return redirect(url_for('view_note'))
    note = Note.query.filter_by(id=note_id, user=current_user).first()
    if note is None:
        flash("No note with that name")
        return redirect(url_for('view_note'))
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for('view_note'))


@app.route("/notes", methods=["POST", "GET"])
def view_notes():
        categories = Category.query.filter_by(user=current_user).all()
        return render_template("note.html", current_user=current_user, categories=categories)

@app.route("/note/<note_id>", methods=['GET', 'POST'])
@app.route("/note", methods=["POST", "GET"])
@login_required
def view_note(note_id=None):
    if request.method == 'GET':
        note = None
        if note_id is not None:
            note = Note.query.filter_by(id=note_id, user=current_user).first()
        categories = Category.query.filter_by(user=current_user).all()
        return render_template("add_note.html", note=note, current_user=current_user, categories=categories)
    elif request.method == 'POST' and note_id is not None:
        note = Note.query.filter_by(id=note_id, user=current_user).first()
        if note is None:
            flash("No note with that name")
            return redirect(url_for('view_notes'))
        category = Category.query.filter_by(name=request.form['category'], user=current_user).first()
        note.name = request.form['name']
        note.category = category
        note.content = request.form['content']
        db.session.commit()
        return redirect(url_for('view_notes'))
    if request.method == 'POST' and note_id is None:
        category = request.form['category']
        name = request.form['name']
        content = request.form['content']
        if not (category and content and name):
            flash("You didn't put in all of the values")
            return redirect(url_for('view_note'))
        category = Category.query.filter_by(name=category, user=current_user).first()
        if category is None:
            flash("No category with that name")
            return redirect(url_for('view_note'))
        new_note = Note(name, category, content, current_user)
        db.session.add(new_note)
        db.session.commit()
        return redirect(url_for('view_notes'))

@app.route("/delete")
@login_required
def delete():
    user = User.query.filter_by(id=current_user.get_id()).first()
    db.session.delete(user)
    logout_user()
    db.session.commit()
    return redirect(url_for('main'))

@app.route("/due_date/<due_date_id>/delete")
@login_required
def delete_due_date(due_date_id):
    if due_date_id is None:
        flash("No due date selected to be deleted")
        return redirect(url_for('main'))
    due_date = Due_date.query.filter_by(id=due_date_id, user=current_user).first()
    if due_date is None:
        flash("No due date with that name")
        return redirect(url_for('main'))
    db.session.delete(due_date)
    db.session.commit()
    return redirect(url_for('main'))

@app.route("/due_date/date/<date>")
@login_required
def create_due_date_date(date):
    if len(date) == 1:
        date = datetime.datetime.now().strftime('%m') + '/0' + date + '/' + str(datetime.datetime.now().year)
    else:
        date = datetime.datetime.now().strftime('%m') + '/' + date + '/' + str(datetime.datetime.now().year)
    categories = Category.query.filter_by(user=current_user).all()
    return render_template("due_date.html", date=date, categories=categories, current_user=current_user, due_date=None)

@app.route("/due_date/<due_date_id>", methods=['GET', 'POST'])
@app.route("/due_date", methods=["POST", "GET"])
@login_required
def view_due_date(due_date_id=None):
    if request.method == 'GET':
        due_date = Due_date.query.filter_by(id=due_date_id, user=current_user).first()
        categories = Category.query.filter_by(user=current_user).all()
        if due_date is not None:
            date = due_date.date.strftime('%m/%d/%Y')
        else:
            date = datetime.datetime.now().strftime('%m/%d/%Y')
        return render_template("due_date.html", due_date=due_date, categories=categories, current_user=current_user, date=date)
    elif request.method == 'POST' and due_date_id is not None:
        due_date = Due_date.query.filter_by(id=due_date_id, user=current_user).first()
        if due_date is None:
            flash("No due date with that name")
            return redirect(url_for('main'))
        category = Category.query.filter_by(name=request.form['category'], user=current_user).first()
        due_date.name = request.form['name']
        due_date.category = category
        due_date.description = request.form['description']
        date = request.form['date']
        due_date.date = datetime.datetime.strptime(date, "%m/%d/%Y")
        db.session.commit()
        month = datetime.datetime.strptime(date, "%m/%d/%Y").strftime("%m")
        return redirect(url_for('main', month=month))
    if request.method == 'POST' and due_date_id is None:
        category = request.form['category']
        date = request.form['date']
        name = request.form['name']
        description = request.form['description']
        if not (category and date and name):
            flash("You didn't put in all of the values")
            return redirect(url_for('main'))
        category = Category.query.filter_by(name=request.form['category'], user=current_user).first()
        if category is None:
            flash("No category with that name")
            return redirect(url_for('main'))
        new_due_date = Due_date(name, category, description, date, current_user)
        db.session.add(new_due_date)
        db.session.commit()
        month = datetime.datetime.strptime(date, "%m/%d/%Y").strftime("%m")
        return redirect(url_for('main', month=month))

@app.route("/both/date/<month>/<day>/<year>")
@login_required
def create_task_and_due_date_date(month, day, year):
    if not (month and day and year):
        flash("Something happened. Not all the values were put in")
        return redirect(url_for('main'))
    if len(day) == 1:
        date = month + '/0' + day + '/' + year
    else:
        date = month + '/' + day + '/' + year
    categories = Category.query.filter_by(user=current_user).all()
    return render_template("both_forms.html", date=date, categories=categories, current_user=current_user, task=None, due_date=None)

@app.route("/task/date/<date>")
@login_required
def create_task_date(date):
    if len(date) == 1:
        date = datetime.datetime.now().strftime('%m') + '/0' + date + '/' + str(datetime.datetime.now().year)
    else:
        date = datetime.datetime.now().strftime('%m') + '/' + date + '/' + str(datetime.datetime.now().year)
    categories = Category.query.filter_by(user=current_user).all()
    return render_template("task.html", date=date, categories=categories, current_user=current_user, task=None)

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
        if request.form.get('completed') == 'on':
            task.completed = True
        else:
            task.completed = False
        date = request.form['date']
        task.date = datetime.datetime.strptime(date, "%m/%d/%Y")
        db.session.commit()
        month = datetime.datetime.strptime(date, "%m/%d/%Y").strftime("%m")
        return redirect(url_for('main', month=month))
    if request.method == 'POST' and task_id is None:
        category = request.form['category']
        date = request.form['date']
        name = request.form['name']
        description = request.form['description']
        if not (category and date and name):
            flash("You didn't put in all of the values")
            return redirect(url_for('main'))
        category = Category.query.filter_by(name=request.form['category'], user=current_user).first()
        if category is None:
            flash("No category with that name")
            return redirect(url_for('main'))
        new_task = Task(name, category, description, date, current_user)
        db.session.add(new_task)
        db.session.commit()
        month = datetime.datetime.strptime(date, "%m/%d/%Y").strftime("%m")
        return redirect(url_for('main', month=month))

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
