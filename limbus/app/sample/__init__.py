from flask import Blueprint

sample = Blueprint("sample", __name__)

from .views import *
