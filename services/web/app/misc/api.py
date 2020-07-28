from . import misc
from .. import db
from flask import request
from ..decorators import token_required
from marshmallow import ValidationError
import json

from .views import (
    new_address_schema,
    new_site_schema,
)

from .models import Address, SiteInformation
from ..auth.models import UserAccount

@misc.route("api/site/new", methods=["POST"])
@token_required
def api_new_site(tokenuser: UserAccount) -> dict:
    values = request.get_json()

    if not values:
        return {"success": False, "message": "No input data provided"}, 400
    
    try:
        result = new_site_schema.load(values)
        