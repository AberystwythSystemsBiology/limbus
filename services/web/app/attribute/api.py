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

from flask import request, current_app
from marshmallow import ValidationError

from ..auth.models import UserAccount
from .models import Attribute
from .views import (
    basic_attributes_schema,
    basic_attribute_schema,
    new_attribute_schema
)

@api.route("/attribute")
@token_required
def attribute_home(tokenuser: UserAccount):
    return success_with_content_response(
        basic_attributes_schema.dumps(Attribute.query.all())
    )

@api.route("/attribute/new", methods=["POST"])
@token_required
def attribute_new_attribute(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    without_specifics = {k: v for (k, v) in values.items() if k in ["term", "description", "type", "element_type"]}

    try:
        result = new_attribute_schema.load(without_specifics)
    except ValidationError as err:
        return validation_error_response(err)

    if without_specifics["type"] == "TEXT":
        pass
    elif without_specifics["type"] == "NUMERIC":
        pass
    else:
        pass

    new_attribute = Attribute(**result)
    new_attribute.created_by = tokenuser.id

    try:
        db.session.add(new_attribute)
        db.session.commit()
        db.session.flush()
        return success_with_content_response(
            basic_attribute_schema.dump(new_attribute)
        )
    except Exception as err:
        return transaction_error_response(err)