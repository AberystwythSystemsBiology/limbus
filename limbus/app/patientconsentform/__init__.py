from flask import Blueprint

pcf = Blueprint("pcf", __name__)

from . import views
