from app.models import db, User, Category
from app.frontend import frontend
from flask import request, render_template, url_for, redirect, flash, abort
from flask.ext.login import login_required, login_user, current_user, logout_user
from hashlib import sha1
from app.forms import RegisterForm, LoginForm

def next_is_valid(next):
    if next ==  '/users':
        if current_user == 'nick':
            return True
        else:
            return False
    elif next is None:
        return True
    else:
        return True

@frontend.route("/delete")
@login_required
def delete():
    user = User.query.filter_by(id=current_user.get_id()).first()
    db.session.delete(user)
    logout_user()
    db.session.commit()
    return redirect(url_for('frontend.main'))

@frontend.route('/users')
@login_required
def list_users():
    if current_user.username == 'nick':
        users = User.query.all()
        return render_template("users.html", users=users)
    else:
        return redirect(url_for('frontend.main'))

@frontend.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            password=form.password.data,
            email=form.email.data,
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
        return redirect(url_for('frontend.main'))

    return render_template('register.html', current_user=current_user, register_form=form)

@frontend.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('frontend.main'))

@frontend.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_user(form.user)
        return redirect(url_for('frontend.main'))
    return render_template('login.html', current_user=current_user, login_form=form)
