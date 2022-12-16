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
    doi2url,
    new_protocol_text_schema,
    basic_protocol_text_schema,
    new_protocol_template_to_document_schema,
    ProtocolTemplateSearchSchema,
)

from ..database import (
    ProtocolTemplate,
    ProtocolText,
    ProtocolTemplateToDocument,
    SampleProtocolEvent,
    DonorProtocolEvent,
)

from ..webarg_parser import use_args, use_kwargs, parser


@api.route("/protocol")
@token_required
def protocol_home(tokenuser: UserAccount):
    return success_with_content_response(
        basic_protocol_templates_schema.dump(ProtocolTemplate.query.all())
    )


@api.route("/protocol/query", methods=["GET"])
@use_args(ProtocolTemplateSearchSchema(), location="json")
@token_required
def protocol_query(args, tokenuser: UserAccount):

    filters, joins = get_filters_and_joins(args, ProtocolTemplate)

    return success_with_content_response(
        basic_protocol_templates_schema.dump(
            ProtocolTemplate.query.filter_by(**filters).filter(*joins).all()
        )
    )


@api.route("/protocol/query_tokenuser/<default_type>", methods=["GET"])
@use_args(ProtocolTemplateSearchSchema(), location="json")
@token_required
def protocol_query_tokenuser(args, tokenuser: UserAccount, default_type="all"):

    filters, joins = get_filters_and_joins(args, ProtocolTemplate)

    protocols = basic_protocol_templates_schema.dump(
        ProtocolTemplate.query.filter_by(**filters).filter(*joins).all()
    )

    choices = []
    settings = tokenuser.settings
    try:
        id0 = settings["data_entry"]["protocol"][default_type]["default"]
        nm0 = None
    except:
        id0 = None

    try:
        choices0 = settings["data_entry"]["protocol"][default_type]["choices"]
        if len(choices0) == 0:
            choices0 = None
    except:
        choices0 = None

    for protocol in protocols:
        if choices0:
            if protocol["id"] not in choices0:
                continue

        if id0 and protocol["id"] == id0:
            nm0 = "LIMBPRO-%i: %s" % (protocol["id"], protocol["name"])
            continue

        choices.append(
            (protocol["id"], "LIMBPRO-%i: %s" % (protocol["id"], protocol["name"]))
        )

    if id0 and nm0:
        # -- Insert default
        choices = [(id0, nm0)] + choices

    print("sett", settings, "default_type", default_type)
    print("choices", choices)
    return success_with_content_response(
        {"info": protocols, "choices": choices, "default": id0}
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
            protocol_template_schema.dump(new_protocol)
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
    protocol_info = protocol_template_schema.dump(
        ProtocolTemplate.query.filter_by(id=id).first()
    )
    protocol_info["doi_url"] = doi2url(protocol_info["doi"])
    return success_with_content_response(protocol_info)


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

@api.route("/protocol/LIMBPRO-<id>/lock", methods=["POST"])
@token_required
def protocol_lock_protocol(id, tokenuser: UserAccount):
    if not tokenuser.is_admin:
        return not_allowed()

    protocol = ProtocolTemplate.query.filter_by(id=id).first()

    if not protocol:
        return not_found("Protocol LIMBPRO-%s" % id)

    protocol.is_locked = not protocol.is_locked
    protocol.update({"editor_id": tokenuser.id})
    try:
        db.session.add(protocol)
        db.session.commit()
    except Exception as err:
        return transaction_error_response(err)

    if protocol.is_locked:
        msg = "Successfully locked protocol!"
    else:
        msg = "Successfully unlocked protocol!"

    return success_with_content_message_response( basic_protocol_text_schema.dump(protocol), msg)

@api.route("/protocol/LIMBPRO-<id>/remove", methods=["POST"])
@token_required
def protocol_remove_protocol(id, tokenuser: UserAccount):
    protocol = ProtocolTemplate.query.filter_by(id=id).first()

    if protocol:
        if protocol.is_locked:
            return locked_response("protocol(%s)" % protocol.id)
    else:
        return not_found("related protocol")

    sample_event = SampleProtocolEvent.query.filter_by(protocol_id=protocol.id).first()
    if sample_event:
        return in_use_response(
            "protocol events (samples %s ...)" % (sample_event.sample_id or "")
        )

    donor_event = DonorProtocolEvent.query.filter_by(protocol_id=protocol.id).first()
    if donor_event:
        return in_use_response(
            "protocol events (donors %s ...)" % (donor_event.donor_id or "")
        )

    try:
        db.session.delete(protocol)
        db.session.commit()
        return success_with_content_message_response(
            {"id": id}, "Protocol successfully deleted!"
        )
    except Exception as err:
        return transaction_error_response(err)
