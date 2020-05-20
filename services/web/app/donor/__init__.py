from flask import Blueprint

donor = Blueprint("donor", __name__)

from . import routes
