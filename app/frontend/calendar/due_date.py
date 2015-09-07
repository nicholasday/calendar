from app.frontend import frontend
from flask.ext.login import login_required, current_user
from flask import url_for, redirect, render_template, flash, request
from app.models import Category, Due_date, db
import datetime

@frontend.route("/due_date/<due_date_id>/delete")
@login_required
def delete_due_date(due_date_id):
    if due_date_id is None:
        flash("No due date selected to be deleted")
        return redirect(url_for('frontend.main'))
    due_date = Due_date.query.filter_by(id=due_date_id, user=current_user).first()
    if due_date is None:
        flash("No due date with that name")
        return redirect(url_for('frontend.main'))
    db.session.delete(due_date)
    db.session.commit()
    return redirect(url_for('frontend.main'))

@frontend.route("/due_date/<due_date_id>", methods=['GET'])
@login_required
def view_due_date(due_date_id):
    due_date = Due_date.query.filter_by(id=due_date_id, user=current_user).first()
    categories = Category.query.filter_by(user=current_user).all()
    if due_date is not None:
        date = due_date.date.strftime('%m/%d/%Y')
    else:
        flash("Due date not found")
        return url_for('frontend.main')
    return render_template("due_date.html", due_date=due_date, categories=categories, current_user=current_user, date=date)

@frontend.route("/due_date", methods=['GET'])
@login_required
def view_due_date_form():
    categories = Category.query.filter_by(user=current_user).all()
    date = datetime.datetime.now().strftime('%m/%d/%Y')
    return render_template("due_date.html", due_date=None, categories=categories, current_user=current_user, date=date)

@frontend.route("/due_date/<due_date_id>", methods=['POST'])
@login_required
def update_due_date(due_date_id):
    due_date = Due_date.query.filter_by(id=due_date_id, user=current_user).first()
    if due_date is None:
        flash("No due date with that name")
        return redirect(url_for('frontend.main'))
    category = Category.query.filter_by(name=request.form['category'], user=current_user).first()
    due_date.name = request.form['name']
    due_date.category = category
    due_date.description = request.form['description']
    date = request.form['date']
    due_date.date = datetime.datetime.strptime(date, "%m/%d/%Y")
    db.session.commit()
    month = datetime.datetime.strptime(date, "%m/%d/%Y").strftime("%m")
    return redirect(url_for('frontend.main', month=month))

@frontend.route("/due_date", methods=["POST"])
@login_required
def create_due_date():
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
    new_due_date = Due_date(name, category, description, date, current_user)
    db.session.add(new_due_date)
    db.session.commit()
    month = datetime.datetime.strptime(date, "%m/%d/%Y").strftime("%m")
    return redirect(url_for('frontend.main', month=month))
