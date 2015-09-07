from app.frontend import frontend
from flask.ext.login import login_required, current_user
from flask import redirect, url_for, render_template, request, flash
from app.models import Category, Note, db
from app.backend.notes import note_delete

@frontend.route("/note/<note_id>/delete")
@login_required
def delete_note(note_id):
    result = note_delete(note_id)
    flash(result['result'])
    return redirect(url_for('frontend.view_notes'))

@frontend.route("/notes")
@login_required
def view_notes():
    categories = Category.query.filter_by(user=current_user).all()
    return render_template("note.html", current_user=current_user, categories=categories)

@frontend.route("/note/<note_id>", methods=['POST'])
@login_required
def update_note(note_id):
    if note_id is not None:
        note = Note.query.filter_by(id=note_id, user=current_user).first()
        if note is None:
            flash("No note with that name")
            return redirect(url_for('frontend.view_notes'))
        category = Category.query.filter_by(name=request.form['category'], user=current_user).first()
        note.name = request.form['name']
        note.category = category
        note.content = request.form['content']
        db.session.commit()
        return redirect(url_for('frontend.view_notes'))

@frontend.route("/note/<note_id>")
@login_required
def view_note(note_id):
    note = None
    if note_id is not None:
        note = Note.query.filter_by(id=note_id, user=current_user).first()
    categories = Category.query.filter_by(user=current_user).all()
    return render_template("add_note.html", note=note, current_user=current_user, categories=categories)

@frontend.route("/note", methods=["POST"])
@login_required
def add_note_post():
    category = request.form['category']
    name = request.form['name']
    content = request.form['content']
    if not (category and content and name):
        flash("You didn't put in all of the values")
        return redirect(url_for('frontend.view_note'))
    category = Category.query.filter_by(name=category, user=current_user).first()
    if category is None:
        flash("No category with that name")
        return redirect(url_for('frontend.view_note'))
    new_note = Note(name, category, content, current_user)
    db.session.add(new_note)
    db.session.commit()
    return redirect(url_for('frontend.view_notes'))

@frontend.route("/note")
@login_required
def add_note_get():
    categories = Category.query.filter_by(user=current_user).all()
    return render_template('add_note.html', note=None, current_user=current_user, categories=categories)
