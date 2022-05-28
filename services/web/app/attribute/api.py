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
from ..api.filters import generate_base_query_filters, get_filters_and_joins
from ..decorators import token_required

from flask import request, current_app, url_for
from marshmallow import ValidationError
from sqlalchemy.sql import func


from ..database import (
    UserAccount,
    Attribute,
    AttributeOption,
    AttributeTextSetting,
    AttributeNumericSetting,
    AttributeData,
    SampleToCustomAttributeData,
    Sample,
)

from .views import (
    attribute_schema,
    basic_attributes_schema,
    basic_attribute_schema,
    new_attribute_schema,
    new_attribute_text_setting_schema,
    new_attribute_numeric_setting_schema,
    new_attribute_option_schema,
    edit_attribute_schema,
    AttributeSearchSchema,
    new_attribute_data_schema,
    attribute_data_schema,
)

from ..webarg_parser import use_args, use_kwargs, parser


@api.route("/attribute", methods=["GET"])
@token_required
def attribute_home(tokenuser: UserAccount):
    return success_with_content_response(
        # basic_attributes_schema.dump(Attribute.query.filter_by(is_locked=False).all())
        basic_attributes_schema.dump(Attribute.query.all())
    )


@api.route("/attribute/query", methods=["GET"])
@use_args(AttributeSearchSchema(), location="json")
@token_required
def attribute_query(args, tokenuser: UserAccount):

    filters, joins = get_filters_and_joins(args, Attribute)

    return success_with_content_response(
        basic_attributes_schema.dump(
            Attribute.query.filter_by(**filters).filter(*joins).all()
        )
    )


@api.route("/attribute/LIMBATTR-<id>", methods=["GET"])
@token_required
def attribute_view_attribute(id, tokenuser: UserAccount):
    attr = Attribute.query.filter_by(id=id).first()
    if not attr:
        return not_found("Attribute LIMBATTR-%s" % id)

    return success_with_content_response(attribute_schema.dump(attr))


@api.route("/attribute/LIMBATTR-<id>/option/new", methods=["POST"])
@token_required
def attribute_new_option(id, tokenuser: UserAccount):
    response, status_code, application = attribute_view_attribute(
        id=id, tokenuser=tokenuser
    )

    if status_code != 200:
        return response.status_code

    elif response["content"]["type"] != "Option":
        return (
            {
                "success": False,
                "messages": "Not suitable for request as this is not an Option Attribute Type.",
            },
            500,
            {"ContentType": "application/json"},
        )

    values = request.get_json()
    values["attribute_id"] = int(id)

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

        print(">>>>>>>>>>> WE ARE HERE")

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
            suppl_result = new_attribute_numeric_setting_schema.load(
                numeric_information
            )
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

        return success_with_content_response(basic_attribute_schema.dump(new_attribute))
    except Exception as err:
        return transaction_error_response(err)


@api.route("/attribute/LIMBATTR-<id>/lock", methods=["POST"])
@token_required
def attribute_lock_attribute(id, tokenuser: UserAccount):
    if not tokenuser.is_admin:
        return not_allowed()

    attribute = Attribute.query.filter_by(id=id).first()

    if not attribute:
        return not_found("Attribute LIMBATTR-%s" % id)

    attribute.is_locked = not attribute.is_locked
    attribute.update({"editor_id": tokenuser.id})
    try:
        db.session.add(attribute)
        db.session.commit()
    except Exception as err:
        return transaction_error_response(err)

    if attribute.is_locked:
        msg = "Successfully locked attribute!"
    else:
        msg = "Successfully unlocked attribute!"

    return success_with_content_message_response(attribute_schema.dump(attribute), msg)


@api.route("/attribute/LIMBATTR-<id>/remove", methods=["POST"])
@token_required
def attribute_remove_attribute(id, tokenuser: UserAccount):
    if not tokenuser.is_admin:
        return not_allowed()

    attribute = Attribute.query.filter_by(id=id).first()

    if not attribute:
        return not_found("Attribute LIMBATTR-%s" % id)

    if attribute.is_locked:
        return locked_response("Attribute LIMBATTR-%s" % id)

    stas = (
        db.session.query(SampleToCustomAttributeData)
        .join(AttributeData)
        .filter(AttributeData.attribute_id == id)
        .distinct(SampleToCustomAttributeData.sample_id)
    )

    ns = stas.count()

    if ns > 0:
        # Print out max 5 sample uuid in message
        stas = stas.with_entities(SampleToCustomAttributeData.sample_id).limit(5).all()
        smpls = db.session.query(Sample.uuid).filter(Sample.id.in_(stas)).all()
        smpls = ", ".join([s[0] for s in smpls])
        return in_use_response("%d samples: %s ..." % (ns, smpls))

    attribute.update({"editor_id": tokenuser.id})

    try:
        db.session.delete(attribute)
        db.session.commit()
    except Exception as err:
        return transaction_error_response(err)

    return success_with_content_response(attribute_schema.dump(attribute))


@api.route("/attribute/LIMBATTR-<id>/option/<option_id>/lock", methods=["POST"])
@token_required
def attribute_lock_option(id, option_id, tokenuser: UserAccount):
    option = AttributeOption.query.filter_by(id=option_id, attribute_id=id).first()

    if not option:
        return {"success": False, "messages": "There's an issue here"}, 417

    option.is_locked = not option.is_locked
    option.editor_id = tokenuser.id
    db.session.add(option)
    db.session.commit()
    db.session.flush()

    # TODO: Replace with an actual attribute option schema.
    return success_with_content_response(new_attribute_option_schema.dump(option))


@api.route("/attribute/LIMBATTR-<id>/edit", methods=["PUT"])
@token_required
def attribute_edit_attribute(id, tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        result = edit_attribute_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    attribute = Attribute.query.filter_by(id=id).first_or_404()
    attribute.editor_id = tokenuser.id
    attribute.updated_on = func.now()

    for attr, value in values.items():
        setattr(attribute, attr, value)

    try:
        db.session.add(attribute)
        db.session.commit()
        db.session.flush()
        return success_with_content_response(basic_attribute_schema.dump(attribute))
    except Exception as err:
        return transaction_error_response(err)


@api.route("/attribute/new/data/<type>", methods=["POST"])
@token_required
def attribute_new_data(type: str, tokenuser: UserAccount):

    if type not in ["text", "option"]:
        return validation_error_response(
            {"Error": "type must be one of text or option."}
        )

    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        if type == "text":
            result = new_attribute_data_schema.load(values)
        elif type == "option":
            result = new_attribute_option_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    attribute_data = AttributeData(**result)
    attribute_data.author_id = tokenuser.id

    try:
        db.session.add(attribute_data)
        db.session.commit()
        db.session.flush()
        return success_with_content_response(attribute_data_schema.dump(attribute_data))
    except Exception as err:
        return transaction_error_response(err)
