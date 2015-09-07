from app.schemas import user_schema, users_schema
from app.backend import backend
from app.models import User
from flask import jsonify

@backend.route('/users/')
def users_get():
    users = User.query.all()
    result = users_schema.dump(users)
    return jsonify({'users': result.data})

@backend.route('/user/<int:id>')
def user_get(id):
    user = User.query.get(id)
    result = user_schema.dump(user)
    return jsonify(result.data)
