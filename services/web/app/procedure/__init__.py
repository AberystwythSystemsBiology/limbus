from flask import Blueprint

procedure = Blueprint("procedures", __name__)

from . import routes
