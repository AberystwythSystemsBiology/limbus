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

from ..database import db, UserAccount

from ..api import api
from ..api.responses import *
from ..api.filters import get_filters_and_joins

from ..decorators import token_required

from flask import request, current_app, jsonify, send_file
from marshmallow import ValidationError


from .views import (
    basic_protocol_templates_schema,
    basic_protocol_template_schema,
    new_protocol_template_schema,
    protocol_template_schema,
    new_protocol_text_schema,
    basic_protocol_text_schema,
    new_protocol_template_to_document_schema,
    ProtocolTemplateSearchSchema
)

from .models import ProtocolTemplate, ProtocolText, ProtocolTemplateToDocument
from ..webarg_parser import use_args, use_kwargs, parser


@api.route("/protocol")
@token_required
def protocol_home(tokenuser: UserAccount):
    return success_with_content_response(
        basic_protocol_templates_schema.dump(ProtocolTemplate.query.all())
    )


@api.route("/document/query", methods=["GET"])
@use_args(ProtocolTemplateSearchSchema(), location="json")
@token_required
def protocol_query(args, tokenuser: UserAccount):
    filters, joins = get_filters_and_joins(args, ProtocolTemplate)

    return success_with_content_response(
        basic_protocol_templates_schema.dump(
            ProtocolTemplate.query.filter_by(**filters).filter(*joins).all())
    )

@api.route("/protocol/new", methods=["POST"])
@token_required
def protocol_new_protocol(tokenuser: UserAccount):

    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        result = new_protocol_template_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    new_protocol = ProtocolTemplate(**result)
    new_protocol.author_id = tokenuser.id

    try:
        db.session.add(new_protocol)
        db.session.commit()
        db.session.flush()

        return success_with_content_response(
            basic_protocol_template_schema.dump(new_protocol)
        )
    except Exception as err:
        print(err)
        return transaction_error_response(err)


@api.route("/protocol/LIMBPRO-<id>/edit", methods=["PUT"])
@token_required
def protocol_edit_protocol(id, tokenuser: UserAccount):
    protocol = ProtocolTemplate.query.filter_by(id=id).first()

    if not protocol:
        return not_found()

    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        result = new_protocol_template_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    for attr, value in values.items():
        setattr(protocol, attr, value)

    protocol.editor_id = tokenuser.id

    try:
        db.session.add(protocol)
        db.session.commit()
        db.session.flush()
        return success_with_content_response(
            basic_protocol_template_schema.dump(protocol)
        )
    except Exception as err:
        return transaction_error_response(err)


@api.route("/protocol/LIMBPRO-<id>/text/new", methods=["POST"])
@token_required
def protocol_new_protocol_text(id, tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        result = new_protocol_text_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    new_text = ProtocolText(**result)
    new_text.protocol_id = id
    new_text.author_id = tokenuser.id

    try:
        db.session.add(new_text)
        db.session.commit()
        db.session.flush()

        return success_with_content_response(basic_protocol_text_schema.dump(new_text))
    except Exception as err:
        return transaction_error_response(err)


@api.route("/protocol/LIMBPRO-<id>")
@token_required
def protocol_view_protocol(id, tokenuser: UserAccount):
    return success_with_content_response(
        protocol_template_schema.dump(ProtocolTemplate.query.filter_by(id=id).first())
    )


@api.route("/protocol/LIMBPRO-<id>/doc/assign", methods=["POST"])
@token_required
def protocol_associate_document(id, tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        result = new_protocol_template_to_document_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    new_association = ProtocolTemplateToDocument(**result)
    new_association.author_id = tokenuser.id

    try:
        db.session.add(new_association)
        db.session.commit()
        db.session.flush()

        return success_with_content_response(
            new_protocol_template_to_document_schema.dump(new_association)
        )
    except Exception as err:
        return transaction_error_response(err)


@api.route("/protocol/LIMBPRO-<id>/text/<t_id>", methods=["GET"])
@token_required
def protocol_view_text(id, t_id, tokenuser: UserAccount):
    return success_with_content_response(
        basic_protocol_text_schema.dump(
            ProtocolText.query.filter_by(id=t_id, protocol_id=id).first()
        )
    )
