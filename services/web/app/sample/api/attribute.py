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

from ...decorators import token_required, requires_roles
from ...misc import get_internal_api_header
from ...webarg_parser import use_args, use_kwargs, parser


from ...database import (
    db,
    UserAccount,
    SampleToCustomAttributeData,
    Sample,
    AttributeData,
)

from ...attribute.views import (
    new_attribute_data_schema,
    new_attribute_option_data_schema,
    attribute_data_schema,
)

import requests


@api.route("/sample/<uuid>/associate/attribute/<type>", methods=["POST"])
# @token_required
@requires_roles("data_entry")
def sample_associate_attribute(uuid: str, type: str, tokenuser: UserAccount) -> str:
    sample_response = requests.get(
        url_for("api.sample_view_sample", uuid=uuid, _external=True),
        headers=get_internal_api_header(tokenuser),
    )

    if sample_response.status_code != 200:
        return sample_response.content

    if type not in ["text", "option", "numeric"]:
        return validation_error_response(
            {"messages": "type must be one of text or option or numeric"}
        )

    values = request.get_json()
    if not values:
        return no_values_response()

    try:
        if type == "text":
            json = new_attribute_data_schema.load(values)
        elif type == "option":
            json = new_attribute_option_data_schema.load(values)
        else:
            json = new_attribute_data_schema.load(values)

    except ValidationError as err:
        return validation_error_response(err)

    attribute_data = AttributeData(**json)
    attribute_data.author_id = tokenuser.id

    try:
        db.session.add(attribute_data)
        db.session.flush()
        attribute_data_id = attribute_data.id
    except Exception as err:
        return transaction_error_response(err)

    stcad = SampleToCustomAttributeData(
        sample_id=sample_response.json()["content"]["id"],
        attribute_data_id=attribute_data_id,
    )

    stcad.author_id = tokenuser.id

    try:
        db.session.add(stcad)
        db.session.commit()
        return success_with_content_response(json)

    except Exception as err:
        return transaction_error_response(err)


@api.route("/sample/<uuid>/attribute/LIMBSCAD-<id>/remove", methods=["POST"])
@api.route("/sample/attribute/LIMBSCAD-<id>/remove", methods=["POST"])
# @token_required
@requires_roles("data_entry")
def sample_remove_attribute_data(id: str, tokenuser: UserAccount, uuid=None) -> str:
    # sta = SampleToCustomAttributeData.query.filter_by(id=id).first()
    stad = AttributeData.query.filter_by(id=id).first()
    if not stad:
        return not_found("attribute data LIMBAD-%s " % id)

    sta = SampleToCustomAttributeData.query.filter_by(attribute_data_id=stad.id).first()
    if not sta:
        return not_found("sample custom attribute for LIMBAD-%s " % id)

    if uuid:
        sample_uuid = db.session.query(Sample.uuid).filter_by(id=sta.sample_id).scalar()
        if not sample_uuid:
            return validation_error_response("Associated sample uuid not matched")
        if sample_uuid != uuid:
            return validation_error_response("Associated sample uuid not matched")

    stad.update({"editor_id": tokenuser.id})
    sta.update({"editor_id": tokenuser.id})
    try:
        db.session.delete(sta)
        db.session.flush()
        db.session.delete(stad)
        db.session.commit()

    except ValidationError as err:
        db.session.rollback()
        return transaction_error_response(err)

    return success_with_content_message_response(
        attribute_data_schema.dump(sta),
        "Sample associated attribute data LIMBSCAD-%s Successfully deleted!" % id,
    )
