from app.frontend import frontend
from flask.ext.login import login_required, current_user
from flask import url_for, redirect, render_template, flash, request
from app.models import Category, Task, db
import datetime

@frontend.route("/task/<task_id>/delete")
@login_required
def delete_task(task_id):
    if task_id is None:
        flash("No task selected to be deleted")
        return redirect(url_for('frontend.main'))
    task = Task.query.filter_by(id=task_id, user=current_user).first()
    if task is None:
        flash("No task with that name")
        return redirect(url_for('frontend.main'))
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('frontend.main'))

@frontend.route("/task/date/<date>")
@login_required
def create_task_date(date):
    if len(date) == 1:
        date = datetime.datetime.now().strftime('%m') + '/0' + date + '/' + str(datetime.datetime.now().year)
    else:
        date = datetime.datetime.now().strftime('%m') + '/' + date + '/' + str(datetime.datetime.now().year)
    categories = Category.query.filter_by(user=current_user).all()
    return render_template("task.html", date=date, categories=categories, current_user=current_user, task=None)

@frontend.route("/task/<task_id>", methods=['GET'])
@login_required
def view_task(task_id):
    task = Task.query.filter_by(id=task_id, user=current_user).first()
    categories = Category.query.filter_by(user=current_user).all()
    if task is not None:
        date = task.date.strftime('%m/%d/%Y')
    else:
        flash("That task couldn't be found")
        return redirect(url_for('frontend.main'))
        date = datetime.datetime.now().strftime('%m/%d/%Y')
    return render_template("task.html", task=task, categories=categories, current_user=current_user, date=date)

@frontend.route("/task/<task_id>", methods=['POST'])
@login_required
def update_task(task_id):
    task = Task.query.filter_by(id=task_id, user=current_user).first()
    if task is None:
        flash("No task with that name")
        return redirect(url_for('frontend.main'))
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
    return redirect(url_for('frontend.main', month=month))

@frontend.route("/task", methods=["GET"])
@login_required
def view_task_form():
    categories = Category.query.filter_by(user=current_user).all()
    date = datetime.datetime.now().strftime('%m/%d/%Y')
    return render_template("task.html", task=None, categories=categories, current_user=current_user, date=date)

@frontend.route("/task", methods=["POST"])
@login_required
def add_task():
    category = request.form['category']
    date = request.form['date']
    name = request.form['name']
    description = request.form['description']
    if not (category and date and name):
        flash("You didn't put in all of the values")
        return redirect(url_for('frontend.main'))
    category = Category.query.filter_by(name=request.form['category'], user=current_user).first()
    if category is None:
        flash("No category with that name")
        return redirect(url_for('frontend.main'))
    max_position = db.session.query(db.func.max(Task.position)).scalar()
    if max_position == None:
        max_position = 1
    else:
        max_position += 1
    #tasks = db.session.query(Task).filter(Task.position == (max_position + 1)).all()
    new_task = Task(name, category, description, date, current_user, max_position)
    db.session.add(new_task)
    db.session.commit()
    month = datetime.datetime.strptime(date, "%m/%d/%Y").strftime("%m")
    return redirect(url_for('frontend.main', month=month))

@frontend.route("/task_position", methods=["POST"])
@login_required
def position_task():
    date = request.form['date']
    positions = request.form.getlist("task")
    for position, id in enumerate(positions):
        task = Task.query.get(id)
        task.position = position
    db.session.commit()
    return

