from flask import Blueprint

sample = Blueprint("sample", __name__)

from . import views