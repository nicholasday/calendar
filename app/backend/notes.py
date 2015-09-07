from app.backend import backend
from app.models import Note, db
from app.schemas import notes_schema, note_schema
from flask import jsonify, redirect, url_for, flash
from flask.ext.login import login_required, current_user

def note_delete(id):
    if id is None:
        return {'action': 'delete', 'note': 'none', 'result':'no note with that id', 'status':'failure'}
    note = Note.query.filter_by(id=id, user=current_user).first()
    if note is None:
        return {'action': 'delete', 'note': 'none', 'result':'no note with that id', 'status':'failure'}
    result = {'note': note_schema.dump(note).data, 'action': 'delete', 'status': 'success', 'result': 'note deleted'}
    db.session.delete(note)
    db.session.commit()
    return result

@backend.route("/note/<int:id>/delete")
@login_required
def backend_note_delete(id):
    result = note_delete(id)
    return jsonify(result)

@backend.route('/notes/')
def notes_get():
    notes = Note.query.all()
    result = notes_schema.dump(notes)
    return jsonify({'notes': result.data})

@backend.route('/note/<int:id>')
def note_get(id):
    note = Note.query.get(id)
    result = note_schema.dump(note)
    return jsonify(result.data)
