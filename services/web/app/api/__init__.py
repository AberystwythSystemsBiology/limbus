from flask import Blueprint

api = Blueprint("api", __name__)

from ..auth.api import *
from ..misc.api import * 