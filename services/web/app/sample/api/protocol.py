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

from flask import request, abort, url_for, flash
from marshmallow import ValidationError
from ...api import api, generics
from ...api.responses import *
from ...decorators import token_required
from ...misc import get_internal_api_header

from ..views import new_sample_protocol_event_schema, sample_protocol_event_schema

from ...database import (
    db,
    SampleProtocolEvent,
    UserAccount,
    Sample,
    Event
)
from ...database import db, SampleProtocolEvent, UserAccount


@api.route("/sample/new/protocol_event", methods=["POST"])
@token_required
def sample_new_sample_protocol_event(tokenuser: UserAccount):
    values = request.get_json()

    print(values)

    if not values:
        return no_values_response()

    try:
        event_result = new_sample_protocol_event_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    new_event = Event(**event_result["event"])
    new_event.author_id = tokenuser.id

    try:
        db.session.add(new_event)
        db.session.commit()
        db.session.flush()
    except Exception as err:
        return transaction_error_response(err)

    new_sample_protocol_event = SampleProtocolEvent(
        sample_id = event_result["sample_id"], 
        event_id = new_event.id,
        author_id = tokenuser.id,
        protocol_id = event_result["protocol_id"]
    )

    try:
        db.session.add(new_sample_protocol_event)
        db.session.commit()
        db.session.flush()

        return success_with_content_response(
            sample_protocol_event_schema.dump(new_sample_protocol_event)
        )

    except Exception as err:
        return transaction_error_response(err)

@api.route("/sample/protocol_event/<uuid>/remove", methods=["POST"])
@token_required
def sample_remove_sample_protocol_event(uuid, tokenuser: UserAccount):

    try:
        protocol_event = SampleProtocolEvent.query.filter_by(uuid=uuid).first()
        if protocol_event.is_locked:
            err = {'messages': 'Protocol Event Locked!'}
            return validation_error_response(err)

        sample_uuid = Sample.query.filter_by(id=protocol_event.sample_id).first().uuid
        print("sample_uuid: ", sample_uuid)

    except:
        flash('Not found')
        return no_values_response()

    try:
        db.session.add(protocol_event)
        db.session.delete(protocol_event)
        db.session.flush()
        db.session.commit()

        flash('Sample protocol event successfully deleted!'),
        return success_with_content_response(
            sample_uuid
        )

    except Exception as err:
        return transaction_error_response(err)
