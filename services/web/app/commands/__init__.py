from flask import Blueprint

cmd_setup = Blueprint("cmd_setup", __name__)

from .setup import *
