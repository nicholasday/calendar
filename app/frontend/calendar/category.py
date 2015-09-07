from app.frontend import frontend
from flask.ext.login import login_required, current_user
from flask import url_for, redirect, render_template, flash, request
from app.models import Category, db

@frontend.route("/category/<category_id>", methods=['GET'])
@frontend.route("/category", methods=["GET"])
@login_required
def view_category(category_id=None):
    category = Category.query.filter_by(id=category_id, user=current_user).first()
    return render_template("category.html", category=category, current_user=current_user)
    
@frontend.route("/category/<category_id>", methods=['POST'])
@login_required
def update_category(category_id):
    category = Category.query.filter_by(id=category_id, user=current_user).first()
    if category is None:
        flash("No category with that name")
        return redirect(url_for('frontend.main'))
    category.name = request.form['name']
    category.color = request.form['color']
    db.session.commit()
    return redirect(url_for('frontend.main'))

@frontend.route("/category", methods=["POST"])
@login_required
def add_category():
    category = request.form['name']
    color = request.form['color']
    if not (category and color):
        flash("You didn't put in all of the values")
        return redirect(url_for('frontend.main'))
    category_search = Category.query.filter_by(name=category, user=current_user).first()
    if category_search is not None:
        flash("You already created a category with that name")
        return redirect(url_for('frontend.main'))
    new_category = Category(category, color, current_user)
    db.session.add(new_category)
    db.session.commit()
    return redirect(url_for('frontend.main'))

@frontend.route("/category/<category_id>/delete")
@login_required
def delete_category(category_id):
    if category_id is None:
        flash("No category selected to be deleted")
        return redirect(url_for('frontend.main'))
    category = Category.query.filter_by(id=category_id, user=current_user).first()
    if category is None:
        flash("No category with that name")
        return redirect(url_for('frontend.main'))
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('frontend.main'))
