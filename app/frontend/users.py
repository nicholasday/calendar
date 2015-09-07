from app.models import db, User, Category
from app.frontend import frontend
from flask import request, render_template, url_for, redirect, flash
from flask.ext.login import login_required, login_user, current_user, logout_user
from hashlib import sha1

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
    if (request.method == 'POST'
            and request.form['username']
            and request.form['password']
            and request.form['email']):

        user = db.session.query(User).filter_by(username=request.form['username']).first()
        if user is not None:
            flash('That username is already taken')
            return redirect(url_for('frontend.main'))
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
            return redirect(url_for('frontend.main'))

    return render_template('login.html', current_user=current_user)

@frontend.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('frontend.main'))

@frontend.route('/login', methods=['GET', 'POST'])
def login():
    if (request.method == 'POST'
            and request.form['username']
            and request.form['password']):

        user = db.session.query(User).filter_by(
            username=request.form['username'],
            password=sha1(request.form['password'].encode('utf-8')).hexdigest()).first()
        if user is None:
            flash("Woah there! You didn't type something in right")
            return redirect(url_for('frontend.main'))
        login_user(user)
        return redirect(url_for('frontend.main'))
    return render_template('login.html', current_user=current_user)
