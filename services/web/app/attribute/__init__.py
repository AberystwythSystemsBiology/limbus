from flask import Blueprint

attribute = Blueprint("attribute", __name__)

from .routes import *
from .api import *
