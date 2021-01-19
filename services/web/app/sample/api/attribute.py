# Copyright (C) 2020  Keiron O'Shea <keo7@aber.ac.uk>
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

from flask import request, abort, url_for
from marshmallow import ValidationError
from ...api import api, generics
from ...api.responses import *
from ...api.filters import generate_base_query_filters, get_filters_and_joins

from ...decorators import token_required
from ...misc import get_internal_api_header
from ...webarg_parser import use_args, use_kwargs, parser


from ...database import db, UserAccount, SampleToCustomAttributeData

from ...attribute.views import (
    new_attribute_data_schema,
    new_attribute_option_schema
)

import requests

@api.route("/sample/<uuid>/associate/attribute/<type>", methods=["POST"])
@token_required
def sample_associate_attribute(uuid: str, type: str, tokenuser: UserAccount) -> str:

    sample_response = requests.get(
        url_for("api.sample_view_sample", uuid=uuid, _external=True),
        headers=get_internal_api_header(tokenuser)
    )

    if sample_response.status_code != 200:
        return sample_response.content

    if type not in ["text", "option"]:
        return validation_error_response({"Error": "type must be one of text or option"})

    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        if type == "text":
            json = new_attribute_data_schema.load(values)
        elif type == "option":
            json = new_attribute_option_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    new_attribute_data_response = requests.post(
        url_for("api.attribute_new_data", type=type, _external=True),
        headers=get_internal_api_header(tokenuser),
        json=json
    )


    if new_attribute_data_response.status_code == 200:

        stcad = SampleToCustomAttributeData(
            sample_id=sample_response.json()["content"]["id"],
            attribute_data_id=new_attribute_data_response.json()["content"]["id"]
        )

        stcad.author_id = tokenuser.id

        try:
            db.session.add(stcad)
            db.session.commit()
            db.session.flush()

            return success_with_content_response({"msg": "custom_attr_data_added"})

        except Exception as err:
            return transaction_error_response(err)

