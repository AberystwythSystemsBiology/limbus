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
    basic_addresses_schema,
    basic_site_schema,
)

from .models import Address, SiteInformation
from ..auth.models import UserAccount


@api.route("/mis/address/", methods=["GET"])
@token_required
def address_home(tokenuser: UserAccount):
    return success_with_content_response(
        basic_addresses_schema(Address.query.all())
    )

@api.route("/misc/address/new", methods=["POST"])
@token_required
def misc_new_address(tokenuser: UserAccount):
    values = request.get_json()

    if values is None:
        return no_values_response()
    try:
        result = new_address_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    new_address = Address(**result)
    new_address.author_id = tokenuser.id

    try:
        db.session.add(new_address)
        db.session.commit()
        db.session.flush()
        return success_with_content_response(basic_address_schema.dumps(new_address))
    except Exception as err:
       return sql_error_response(err)

@api.route("/mis/site/new", methods=["GET"])
@token_required
def misc_new_site(tokenuser: UserAccount):
    values = request.get_json()

    if values is None:
        return no_values_response()

    try:
        result = new_site_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)
    
    new_site = SiteInformation(**result)
    new_site.author_id = tokenuser.id

    try:
        db.session.add(new_site)
        db.session.commit()
        db.session.flush()
        return success_with_content_response(basic_site_schema.dumps(new_site))
    except Exception as err:
        return sql_error_response(err)