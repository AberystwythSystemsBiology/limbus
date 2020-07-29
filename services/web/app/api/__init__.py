from .. import spec
from flask import Blueprint

api = Blueprint("api", __name__)

from ..auth.api import *
from ..misc.api import * 

def no_values_response():
    return {"success": False, "message": "No input data provided"}, 400

def validation_error_response(err):
    return {"success": False, "messages" : err.messages}, 417
    
def sql_error_response(err):
    return {"success": False, "message": str(err.orig.diag.message_primary)}, 417

def success_with_content(content):
    return {"success": True, "content": content}, 200

def success_without_content():
    return {"success": True}, 200

@api.route("/")
def api_doc():
    return spec.to_dict()   