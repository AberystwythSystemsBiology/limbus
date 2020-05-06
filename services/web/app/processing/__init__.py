from flask import Blueprint

processing = Blueprint("processing", __name__)

from . import routes
