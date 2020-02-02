from flask import Blueprint

demo = Blueprint("demo", __name__)

from . import views