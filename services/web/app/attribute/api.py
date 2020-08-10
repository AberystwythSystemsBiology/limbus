# Copyright (C) 2019  Keiron O'Shea <keo7@aber.ac.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from ..api import api, db
from ..api.responses import *
from ..decorators import token_required

from flask import request, current_app, url_for
from marshmallow import ValidationError

from ..auth.models import UserAccount
from .models import (
        Attribute,
        AttributeTextSetting,
        AttributeNumericSetting,
        AttributeOption,
        )

from .views import (
    attribute_schema,
    basic_attributes_schema,
    basic_attribute_schema,
    new_attribute_schema,
    new_attribute_text_setting_schema,
    new_attribute_numeric_setting_schema,
    new_attribute_option_schema,
)

import requests
from ..misc import get_internal_api_header


@api.route("/attribute", methods=["GET"])
@token_required
def attribute_home(tokenuser: UserAccount):
    return success_with_content_response(
        basic_attributes_schema.dump(Attribute.query.all())
    )

@api.route("/attribute/LIMBATTR-<id>", methods=["GET"])
@token_required
def attribute_view_attribute(id, tokenuser: UserAccount):
    return success_with_content_response(
        attribute_schema.dump(Attribute.query.filter_by(id=id).first_or_404())
    )

@api.route("/attribute/LIMBATTR-<id>/option/new", methods=["POST"])
@token_required
def attribute_new_option(id, tokenuser: UserAccount):
    response, status_code, application = attribute_view_attribute(id=id, tokenuser=tokenuser)   
    print(status_code)

    if status_code != 200:
        return response.status_code
    
    elif response["content"]["type"] != "OPTION":
        return {"success": False, "messages": "Not an option value"}, 500, {"ContentType": "application/json"}

    values = request.get_json()

    if not values:
        return no_values_response()
    
    try:
        option_result = new_attribute_option_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    new_option = AttributeOption(**option_result)
    new_option.author_id = tokenuser.id
    new_option.attribute_id = id
    try:
        db.session.add(new_option)
        db.session.commit()
        
        return success_with_content_response(
                attribute_schema.dump(Attribute.query.filter_by(id=id).first())
                )
    except Exception as err:
        return transaction_error_response(err)
    

@api.route("/attribute/new", methods=["POST"])
@token_required
def attribute_new_attribute(tokenuser: UserAccount):

    values = request.get_json()

    if not values:
        return no_values_response()

    attribute_information = values["attribute_information"]
    try:
        attr_result = new_attribute_schema.load(attribute_information)
    except ValidationError as err:
        return validation_error_response(err)


    try:
        if attribute_information["type"] == "TEXT":
            text_information = values["additional_information"]
            suppl_result = new_attribute_text_setting_schema.load(text_information)
            suppl_obj = AttributeTextSetting
        elif attribute_information["type"] == "NUMERIC":
            numeric_information = values["additional_information"]
            suppl_result = new_attribute_numeric_setting_schema.load(numeric_information)
            suppl_obj = AttributeNumericSetting
    except ValidationError as err:
        return validation_error_response(err)
    
    new_attribute = Attribute(**attr_result)
    new_attribute.author_id = tokenuser.id

    try:
        db.session.add(new_attribute)      
        db.session.flush()

        if attribute_information["type"] != "OPTION":
            new_suppl = suppl_obj(**suppl_result)
            new_suppl.author_id = tokenuser.id
            new_suppl.attribute_id = new_attribute.id

            db.session.add(new_suppl)
            db.session.flush()

        db.session.commit()

        return success_with_content_response(
            basic_attribute_schema.dump(new_attribute)
        )
    except Exception as err:
        return transaction_error_response(err)
