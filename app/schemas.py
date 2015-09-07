from .models import User, Category, Task, Note, Due_date
from app import ma
from flask_marshmallow.sqla import HyperlinkRelated

class UserSchema(ma.ModelSchema):
    class Meta:
        model = User

class CategorySchema(ma.ModelSchema):
    class Meta:
        model = Category
    user = HyperlinkRelated('backend.user_get')

class TaskSchema(ma.ModelSchema):
    class Meta:
        model = Task
    user = HyperlinkRelated('backend.user_get')

class NoteSchema(ma.ModelSchema):
    class Meta:
        model = Note
    user = HyperlinkRelated('backend.user_get')

class Due_dateSchema(ma.ModelSchema):
    class Meta:
        model = Due_date
    user = HyperlinkRelated('backend.user_get')

users_schema = UserSchema(many=True)
user_schema = UserSchema()
categories_schema = CategorySchema(many=True)
category_schema = CategorySchema()
tasks_schema = TaskSchema(many=True)
task_schema = TaskSchema()
notes_schema = NoteSchema(many=True)
note_schema = NoteSchema()
due_dates_schema = Due_dateSchema(many=True)
due_date_schema = Due_dateSchema()
