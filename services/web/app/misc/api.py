from . import misc
from .. import db
from flask import request
from ..decorators import token_required
from marshmallow import ValidationError
import json

from ..api import api
from ..api.responses import *


from .views import (
    new_address_schema,
    new_site_schema,
    basic_address_schema,
)

from .models import Address, SiteInformation
from ..auth.models import UserAccount


@api.route("/mis/address/new", methods=["POST"])
@token_required
def misc_new_address(tokenuser: UserAccount):
    values = request.get_json()

    try:
        result = new_address_schema.load(values)
    except ValidationError:
        return validation_error_response(err)

    new_address = Address(**result)
    new_address.created_by = tokenuser.id

    try:
        db.session.add(address)
        db.session.commit()
        db.session.flush()
        return success_with_content_response(basic_address_schema.dumps(new_address))
    except Exception as err:
        return sql_error_response(err)
