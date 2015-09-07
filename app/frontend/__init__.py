from flask import Blueprint

frontend = Blueprint('frontend', __name__, template_folder='templates')

import app.frontend.calendar
import app.frontend.users
import app.frontend.notes
