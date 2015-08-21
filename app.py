from flask import Flask, render_template, url_for, redirect, request
import datetime
import calendar
from flask.ext.sqlalchemy import SQLAlchemy
app = Flask(__name__)

# use a database per day
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class _localized_month:
    _months = [datetime.date(2001, i+1, 1).strftime for i in range(12)]
    _months.insert(0, lambda x: "")

    def __init__(self, format):
        self.format = format

    def __getitem__(self, i):
        funcs = self._months[i]
        if isinstance(i, slice):
            return [f(self.format) for f in funcs]
        else:
            return funcs(self.format)

    def __len__(self):
        return 13

cssclasses = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
month_name = _localized_month('%B')

def make_html_calendar(calendar):
    v = []
    a = v.append
    a('<table border="0" cellpadding="0" cellspacing="0" class="month">')
    a('\n')
    a(formatmonthname(datetime.datetime.now().month, datetime.datetime.now().month))
    a('\n')
    a(formatweekheader())
    a('\n')
    for week in calendar:
        a(formatweek(week))
        a('\n')
    a('</table>')
    a('\n')
    return ''.join(v)

def formatday(day, weekday):
    if day[0] == 0:
        return '<td class="noday">&nbsp;</td>' # day outside month
    else:
        s = str(day[0]) + "<ol>"
        for i in range(1, len(day)):
            s = s + "<li>" + str(day[i]) + "</li>"

        if day[0] == datetime.datetime.now().day:
            day_class = 'today'
        else:
            day_class = cssclasses[weekday]

        return '<td class="%s">%s</ol></td>' % (day_class, s)

def formatweek(theweek):
    s = ''
    for d in theweek:
        #s = s + formatday(d, 1)
        s = s + formatday(d, datetime.datetime.today().weekday())
    return '<tr>%s</tr>' % s

def formatweekday(day):
    return '<th class="%s">%s</th>' % (cssclasses[day], cssclasses[day])

def formatweekheader():
    s = ''.join(formatweekday(i) for i in range(0,7))
    return '<tr>%s</tr>' % s

def formatmonthname(theyear, themonth, withyear=True):
    if withyear:
        s = '%s %s' % (month_name[themonth], theyear)
    else:
        s = '%s' % month_name[themonth]
    return '<tr><th colspan="7" class="month">%s</th></tr>' % s

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    color = db.Column(db.String(80))

    def __init__(self, name, color):
        self.name = name
        self.color = color

    def __repr__(self):
        return '<Category %r>' % self.name

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship("Category", backref=db.backref('tasks', lazy="dynamic"))
    date = db.Column(db.DateTime)
    description = db.Column(db.Text)

    def __init__(self, name, category, description, date):
        self.name = name
        self.category = category
        self.description = description
        self.date = datetime.datetime.strptime(date, "%m/%d/%Y")

    def __repr__(self):
        return '<Task %r>' % self.name

@app.route('/')
def main():
    categories = Category.query.all()
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
                           day.append(task.name) 

    html_calendar = make_html_calendar(new_list_calendar)
    return render_template('index.html', categories=categories, calendar=html_calendar, task=None)

@app.route("/category", methods=["POST"])
def create_category():
    if request.method == 'POST':
        category = request.form['category']
        color = request.form['color']
        if not (category and color):
            return "You didn't put in all of the values"
        category_search = Category.query.filter_by(name=category).first()
        if category_search is not None:
            return "You already created a category with that name"
        new_category = Category(category, color)
        db.session.add(new_category)
        db.session.commit()
        return redirect(url_for('main'))

@app.route("/task", methods=["POST"])
def create_task():
    if request.method == 'POST':
        category = request.form['category']
        date = request.form['date']
        name = request.form['name']
        description = request.form['description']
        if not (category and date and name and description):
            return "You didn't put in all of the values"
        category = Category.query.filter_by(name=request.form['category']).first()
        if category is None:
            return "No category with that name"
        new_task = Task(name, category, description, date)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('main'))

@app.route("/task/<task_id>/delete")
def delete_task(task_id):
    if task_id is None:
        return "No task selected to be deleted"
    task = Task.query.filter_by(id=task_id).first()
    if task is None:
        return "No task with that name"
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('main'))

@app.route("/task/<task_id>", methods=['GET', 'POST'])
def view_task(task_id):
    if request.method == 'GET':
        if task_id is None:
            return "No task selected"
        task = Task.query.get(task_id)
        if task is None:
            return "No task with that name"
        categories = Category.query.all()
        return render_template("task.html", task=task, categories=categories)
    elif request.method == 'POST':
        if task_id is None:
            return "No task selected"
        task = Task.query.get(task_id)
        if task is None:
            return "No task with that name"
        category = Category.query.filter_by(name=request.form['category']).first()
        task.name = request.form['name']
        task.category = category
        task.description = request.form['description']
        task.date = datetime.datetime.strptime(request.form['date'], "%m/%d/%Y")
        db.session.commit()
        #categories = Category.query.all()
        #return render_template("task.html", task=task, categories=categories)
        return redirect(url_for('main'))

@app.route("/category/<category_id>/delete")
def delete_category(category_id):
    if category_id is None:
        return "No category selected to be deleted"
    category = Category.query.filter_by(id=category_id).first()
    if category is None:
        return "No category with that name"
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('main'))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
