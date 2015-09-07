from flask import Blueprint

backend = Blueprint('backend', __name__, template_folder='templates', url_prefix="/api")

import app.backend.calendar
import app.backend.users
import app.backend.notes
