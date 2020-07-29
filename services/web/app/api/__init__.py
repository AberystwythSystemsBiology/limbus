from .. import spec
from flask import Blueprint

api = Blueprint("api", __name__)

from ..auth.api import *
from ..misc.api import *

from .responses import *


@api.route("/")
def api_doc():
    return spec.to_dict()
