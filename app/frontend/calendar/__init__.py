from app.frontend import frontend
from flask.ext.login import current_user, login_required
from app.models import User, Category, Task, Due_date, db
from flask import render_template, redirect, url_for, flash, request
import datetime
import calendar

import app.frontend.calendar.due_date
import app.frontend.calendar.task
import app.frontend.calendar.category

@frontend.route('/date/<int:month>')
@frontend.route('/date/<int:month>/<int:week_number>')
@frontend.route('/date/<int:month>/<int:week_number>/<int:year>')
@frontend.route('/user/<user_id>')
@frontend.route('/user/<user_id>/date/<int:month>')
@frontend.route('/user/<user_id>/date/<int:month>/<int:week_number>')
@frontend.route('/user/<user_id>/date/<int:month>/<int:week_number>/<int:year>')
@frontend.route('/')
def main(user_id=None, month=None, week_number=None, year=None):
    if user_id and current_user.username == 'nick':
        logged_in_user = User.query.filter_by(id=user_id).first()
    else:
        if current_user.is_authenticated():
            logged_in_user = current_user
        else:
            logged_in_user = User.query.filter_by(username='nick').first()
    categories = Category.query.filter_by(user=logged_in_user).all()
    due_dates = Due_date.query.filter_by(user=logged_in_user).all()
    tasks = Task.query.filter_by(user=logged_in_user).order_by(Task.position).all()
    #categories = (db.session.query(Category).
    #    filter_by(user=logged_in_user).
    #    join(Task, Category.tasks).
    #    order_by(Task.position)
    #    )

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

    for due_date in due_dates:
        if due_date.date.month == month:
            for week in new_list_calendar:
                for day in week:
                    if day[0] == due_date.date.day and month == due_date.date.month and year == due_date.date.year:
                        day.append([due_date.category.color, due_date.id, 'due_date', due_date.name]) 
    
    for task in tasks:
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

@frontend.route("/both/date/<month>/<day>/<year>")
@login_required
def create_task_and_due_date_date(month, day, year):
    if not (month and day and year):
        flash("Something happened. Not all the values were put in")
        return redirect(url_for('frontend.main'))
    if len(day) == 1:
        date = month + '/0' + day + '/' + year
    else:
        date = month + '/' + day + '/' + year
    categories = Category.query.filter_by(user=current_user).all()
    completed = 0
    tasks_number = 0
    for category in categories:
        for task in category.tasks:
            if task.date.strftime('%m/%d/%Y') == datetime.datetime.now().strftime("%m/%d/%Y"):
                tasks_number += 1
                if task.completed == True:
                    completed += 1
    return render_template("both_forms.html", completed=completed, tasks_number=tasks_number, date=date, categories=categories, current_user=current_user, task=None, due_date=None)
