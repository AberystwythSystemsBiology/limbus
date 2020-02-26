from flask import Blueprint

document = Blueprint("document", __name__)

from . import views
