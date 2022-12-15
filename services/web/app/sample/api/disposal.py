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
from .base import func_update_sample_status
from ...decorators import token_required
from ...misc import get_internal_api_header, flask_return_union
from datetime import datetime

from ..views import (
    new_sample_disposal_schema,
    basic_disposal_schema,
    sample_disposal_schema,
    new_sample_disposal_event_schema,
    basic_sample_disposal_event_schema,
    new_sample_protocol_event_schema,
)
from ..enums import DisposalInstruction
from ...database import (
    db,
    SampleDisposal,
    UserAccount,
    SampleDisposalEvent,
    Sample,
    Event,
    SampleProtocolEvent,
    EntityToStorage,
    UserCart,
)

import requests


@api.route("/sample/new/disposal_instructions", methods=["POST"])
@token_required
def sample_new_disposal_instructions(tokenuser: UserAccount) -> flask_return_union:
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        disposal_instructions_values = new_sample_disposal_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    new_disposal_instructions = SampleDisposal(**disposal_instructions_values)
    new_disposal_instructions.author_id = tokenuser.id

    try:
        db.session.add(new_disposal_instructions)
        db.session.commit()
        db.session.flush()

        return success_with_content_response(
            basic_disposal_schema.dump(new_disposal_instructions)
        )
    except Exception as err:
        return transaction_error_response(err)


def func_new_sample_disposal(tokenuser: UserAccount, values, new_event=None):
    success = True

    sample_uuid = values.pop("sample_uuid", None)
    sample_id = values.pop("sample_id", None)

    if sample_id:
        sample = Sample.query.filter_by(id=sample_id).first()
    else:
        sample = Sample.query.filter_by(uuid=sample_uuid).first()

    if not sample:
        success = False
        message = "Sample %s not found" % (sample_uuid or sample_id)
        return success, message, None, None

    if sample.is_locked:
        success = False
        message = "Sample %s is locked " % (sample_uuid or sample_id)
        return success, message, None, None

    if sample.is_closed:
        success = False
        message = "Sample %s is closed " % (sample_uuid or sample_id)
        return success, message, None, None

    # Step 1 Check sample disposal instruction
    # Step 2 add new protocol event
    # Step 3 update disposal instruction table
    # Step 4 update storage: delete association to lts/rack
    # Step 5 update sample status

    disposal = SampleDisposal.query.filter_by(id=sample.disposal_id).first()

    if disposal is None:
        success = False
        message = "Disposal instruction not found for sample %s" % (sample.uuid)
        return success, message, None, None

    if disposal.instruction not in [DisposalInstruction.DES, DisposalInstruction.TRA]:
        success = False
        message = "No instruction of destruction or transferring for sample %s" % (
            sample.uuid
        )
        return success, message, None, None

    if disposal.disposal_date > datetime.now().date():
        success = False
        message = "Too early to dispose for sample %s, expected disposal date: %s" % (
            sample.uuid,
            disposal.disposal_date,
        )
        return success, message, None, None

    sample_id = sample.id
    protocolevent_values = {
        "event": values["event"],
        "protocol_id": values["protocol_id"],
        "sample_id": sample.id,
        "reduced_quantity": 0,  # sample.remaining_quantity,
    }

    try:
        event_result = new_sample_protocol_event_schema.load(protocolevent_values)
    except ValidationError as err:
        success = False
        message = "New protocol event validation error for sample %s: %s" % (
            sample.uuid,
            str(err),
        )
        return success, message, None, None

    if not new_event:
        new_event = Event(**event_result["event"])
        new_event.author_id = tokenuser.id

        try:
            db.session.add(new_event)
            db.session.flush()
        except Exception as err:
            success = False
            message = "New event transaction error for sample %s: %s" % (
                sample.uuid,
                str(err),
            )
            return success, message, None, None

    new_sample_protocol_event = SampleProtocolEvent(
        sample_id=event_result["sample_id"],
        event_id=new_event.id,
        author_id=tokenuser.id,
        protocol_id=event_result["protocol_id"],
    )

    try:
        db.session.add(new_sample_protocol_event)
        db.session.flush()

        disposal.disposal_event_id = new_sample_protocol_event.id
        disposal.editor_id = tokenuser.id
        db.session.add(disposal)
    except Exception as err:
        success = False
        message = "New protocol event transaction error for sample %s: %s" % (
            sample.uuid,
            str(err),
        )
        return success, message, new_event, None

    try:
        disposal_event_values = new_sample_disposal_event_schema.load(
            {
                "sample_id": sample_id,
                "reason": values["reason"],
                "protocol_event_id": new_sample_protocol_event.id,
            }
        )
    except ValidationError as err:
        success = False
        message = "New disposal event validation error for sample %s: %s" % (
            sample.uuid,
            str(err),
        )
        return success, message, new_event, new_sample_protocol_event

    new_disposal_event = SampleDisposalEvent(**disposal_event_values)
    new_disposal_event.author_id = tokenuser.id

    try:
        db.session.add(new_disposal_event)
        db.session.flush()

    except Exception as err:
        success = False
        message = "New disposal event transaction error for sample %s: %s" % (
            sample.uuid,
            str(err),
        )
        return success, message, new_event, disposal

    ets = EntityToStorage.query.filter_by(sample_id=sample_id).all()

    if ets:
        try:
            for et in ets:
                db.session.delete(et)
        except Exception as err:
            success = False
            message = "Storage removal for sample %s transaction error : %s" % (
                sample.uuid,
                str(err),
            )
            return success, message, new_event, disposal

    scs = UserCart.query.filter_by(sample_id=sample_id).all()

    if scs:
        try:
            for sc in scs:
                db.session.delete(sc)
        except Exception as err:
            success = False
            message = "Removal from carts for sample %s transaction error : %s" % (
                sample.uuid,
                str(err),
            )
            return success, message, new_event, disposal

    sample_status_events = {"sample_disposal": disposal}

    # -- Sample status update
    res = func_update_sample_status(
        tokenuser=tokenuser, auto_query=True, sample=sample, events=sample_status_events
    )

    if res["success"] is True and res["sample"]:
        try:
            db.session.add(res["sample"])

            message = "Sample %s successfully disposed! " % sample.uuid
            message = message + " | " + res["message"]
            return success, message, new_event, disposal

        except Exception as err:
            success = False
            message = "Errors in updating sample after disposal for sample %s: %s." % (
                sample.uuid,
                str(err),
            )
            message = message + " | " + res["message"]
            return success, message, new_event, new_sample_protocol_event

    message = "Successfully dispose sample %s." % sample.uuid
    message = message + " | " + res["message"]
    return success, message, new_event, disposal


@api.route("/sample/new/disposal_event", methods=["POST"])
@token_required
def sample_new_disposal_event(tokenuser: UserAccount) -> flask_return_union:
    values: dict = request.get_json()

    if not values:
        return no_values_response()

    success, message, new_event, disposal = func_new_sample_disposal(
        tokenuser, values, None
    )

    if success:
        try:
            db.session.commit()
            return success_with_content_message_response(
                sample_disposal_schema.dump(disposal), message
            )
        except Exception as err:
            return transaction_error_response(err)
    else:
        return validation_error_response(message)


@api.route("/sample/batch/disposal_event", methods=["POST"])
@token_required
def sample_batch_disposal_event(tokenuser: UserAccount) -> flask_return_union:

    cart = UserCart.query.filter_by(author_id=tokenuser.id, selected=True).all()

    if len(cart) == 0:
        return validation_error_response("No sample selected in cart!")

    values = request.get_json()

    if not values:
        return no_values_response()

    # print("values: ", values)
    new_event = None
    msgs = []
    for sc in cart:
        values["sample_id"] = sc.sample_id
        success, message, new_event, disposal = func_new_sample_disposal(
            tokenuser, values, new_event
        )

        if not success:
            return {"success": False, "message": message}

        msgs.append(message)

    try:
        db.session.commit()
        return success_with_content_message_response({}, msgs)
    except Exception as err:
        return transaction_error_response(err)
