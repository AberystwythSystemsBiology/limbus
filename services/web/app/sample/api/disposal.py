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

from ..views import (
    new_sample_disposal_schema,
    basic_disposal_schema,
    new_sample_disposal_event_schema,
    basic_sample_disposal_event_schema,
    new_sample_protocol_event_schema,
)

from ...database import (
    db, SampleDisposal, UserAccount,
    SampleDisposalEvent, Sample,
    Event, SampleProtocolEvent,
    EntityToStorage)

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


@api.route("/sample/new/disposal_event", methods=["POST"])
@token_required
def sample_new_disposal_event(tokenuser: UserAccount) -> flask_return_union:
    values: dict = request.get_json()

    if not values:
        return no_values_response()

    sample_response = requests.get(
        url_for("api.sample_view_sample", uuid=values["sample_uuid"], _external=True),
        headers=get_internal_api_header(tokenuser),
    )

    if sample_response.status_code == 200:
        # Step 1 Check sample disposal instruction
        # -- if disposal date approached: proceed to step 2 otherwise, stop with warning date
        # Step 2 add new protocol event
        # Step 3 update disposal instruction table
        # Step 4 update storage: delete association to lts/rack
        # Step 5 update sample status

        # sample_id = sample_response.json()["content"]["id"]
        remaining_quantity = sample_response.json()["content"]["remaining_quantity"]
        protocolevent_values = {"event" : values["event"],
                  "protocol_id": values["protocol_id"],
                  "sample_id": sample_id,
                  "reduced_quantity": 0 #remaining_quantity,
                  }

        try:
            event_result = new_sample_protocol_event_schema.load(protocolevent_values)
        except ValidationError as err:
            return validation_error_response(err)

        new_event = Event(**event_result["event"])
        new_event.author_id = tokenuser.id

        try:
            db.session.add(new_event)
            db.session.flush()
        except Exception as err:
            return transaction_error_response(err)

        new_sample_protocol_event = SampleProtocolEvent(
            sample_id=event_result["sample_id"],
            event_id=new_event.id,
            author_id=tokenuser.id,
            protocol_id=event_result["protocol_id"],
        )

        try:
            db.session.add(new_sample_protocol_event)
            db.session.flush()
        except Exception as err:
            return transaction_error_response(err)


        try:
            disposal_event_values = new_sample_disposal_event_schema.load(
                {
                    "sample_id" : sample_id,
                    "reason": values["reason"],
                    "protocol_event_id": new_sample_protocol_event.id
                }
            )
        except ValidationError as err:
            return validation_error_response(err)

        new_disposal_event = SampleDisposalEvent(**disposal_event_values)
        new_disposal_event.author_id = tokenuser.id

        try:
            db.session.add(new_disposal_event)
        except ValidationError as err:
            return validation_error_response(err)

        sample = Sample.query.filter_by(
            uuid=sample_response.json()["content"]["uuid"]
        ).first()

        disposal_instruction = SampleDisposal.query.filter_by(id = sample.disposal_id).first()
        disposal_instruction.disposal_event_id = new_sample_protocol_event.id
        disposal_instruction.editor_id = tokenuser.id

        ets = EntityToStorage.query.filter_by(sample_id=sample_id).all()

        if ets:
            try:
                for et in ets:
                    db.session.delete(et)
            except ValidationError as err:
                return validation_error_response(err)

        sample_status_events = {"sample_disposal": disposal_instruction}

        try:
            res = func_update_sample_status(tokenuser=tokenuser, auto_query=True, sample=sample,
                                            events=sample_status_events)

            message = "Sample successfully disposed! " + res["message"]
            if res["success"] is True and res["sample"]:
                db.session.add(sample)

            db.session.commit()
            return success_with_content_message_response(
                basic_sample_disposal_event_schema.dump(new_disposal_event), message
            )

        except Exception as err:
            return transaction_error_response(err)


    else:
        return sample_response.content
