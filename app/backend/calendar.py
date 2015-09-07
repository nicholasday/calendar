from app.schemas import category_schema, categories_schema
from app.models import Category
from app.backend import backend
from flask import jsonify

@backend.route('/categories/')
def categories_get():
    categories = Category.query.all()
    result = categories_schema.dump(categories)
    return jsonify({'categories': result.data})

@backend.route('/category/<int:id>')
def category_get(id):
    category = Category.query.get(id)
    result = category_schema.dump(category)
    return jsonify(result.data)

