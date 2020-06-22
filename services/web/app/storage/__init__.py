from flask import Blueprint

storage = Blueprint("storage", __name__)

from .routes import *
