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
from .queries import func_remove_aliquot_subsampletosample_children, func_remove_sample
from ..views import new_sample_protocol_event_schema, sample_protocol_event_schema

from ...database import db, SampleProtocolEvent, UserAccount, Sample, Event, ProtocolTemplate
from ...protocol.enums import ProtocolType


@api.route("/sample/new/protocol_event", methods=["POST"])
@token_required
def sample_new_sample_protocol_event(tokenuser: UserAccount):
    values = request.get_json()

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
        #db.session.commit()
        db.session.flush()
    except Exception as err:
        return transaction_error_response(err)

    event_result.pop("event")
    new_sample_protocol_event = SampleProtocolEvent(**event_result)
    new_sample_protocol_event.author_id = tokenuser.id
    new_sample_protocol_event.event_id = new_event.id
    # new_sample_protocol_event = SampleProtocolEvent(
    #     sample_id=event_result["sample_id"],
    #     event_id=new_event.id,
    #     author_id=tokenuser.id,
    #     protocol_id=event_result["protocol_id"],
    # )

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
    protocol_event = SampleProtocolEvent.query.filter_by(uuid=uuid).first()
    if not protocol_event:
        return not_found("protocol event(%s)" % uuid)

    # if protocol_event.is_locked:
    #      return locked_response("protocol event! ")

    protocol_event_id = protocol_event.id
    sample = Sample.query.filter_by(id=protocol_event.sample_id).first()

    if sample:
        if sample.is_locked:
            return locked_response("sample(%s)" % sample.uuid)
    else:
        return not_found("related sample")

    sample_uuid = sample.uuid
    msgs = []
    protocol_type = ProtocolTemplate.query.filter_by(id=protocol_event.protocol_id).first().type
    if protocol_type == ProtocolType.ALD:
        # - remove protocol event and the sub-samples it generated
        print('ok00')
        (success, msgs) = func_remove_aliquot_subsampletosample_children(
                                     sample, protocol_event, msgs)
        print('msgs00', msgs)
        if not success:
            return msgs[-1]

    elif protocol_event.is_locked:
        # and protocol_type in [ProtocolType.ACQ, ProtocolType.STU, ProtocolType.COL, ProtocolType.TMP):
        # -- remove protocol event and the sample it generated
        print('ok00')
        (success, msgs) = func_remove_sample(sample, msgs)
        print('msgs00', msgs)
        if not success:
            return msgs[-1]

        elif protocol_type in [ProtocolType.SDE, ProtocolType.STR]:
            err = {"messages": "Type of protocol events (%s) not allowed!" % protocol_type}
            return validation_error_response(err)

    try:
        db.session.delete(protocol_event)
        db.session.commit()
        msgs.append("Sample protocol event (%s) deleted successfully! " % uuid)
        message = ' | '.join(msgs)

        return success_with_content_message_response(uuid, message)
    except Exception as err:
        db.session.rollback()
        return(transaction_error_response(err))

    # -- CASCADE DELETE with protocol event defined in model
    # -- No need to delete separately
    # event = None
    # if protocol_event.event_id:
    #     event = Event.query.filter_by(id=protocol_event.event_id).first()
    # try:
    #     if event:
    #         db.session.delete(event)
    #     db.session.commit()
    #     return success_with_content_response(sample_uuid)
    #
    # except Exception as err:
    #     return transaction_error_response(err)

