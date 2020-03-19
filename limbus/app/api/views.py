from . import api

from .. import db
from flask import (
    redirect,
    render_template,
    url_for,
    abort,
    current_app,
    send_file,
    jsonify,
)
from flask_login import login_required, current_user
from datetime import datetime

from ..document.models import Document



