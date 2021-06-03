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
from ...decorators import token_required
from ...misc import get_internal_api_header, flask_return_union

from ..views import (
    new_sample_disposal_schema,
    basic_disposal_schema,
    new_sample_disposal_event_schema,
    basic_sample_disposal_event_schema,
)

from ...database import db, SampleDisposal, UserAccount, SampleDisposalEvent, Sample

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

        new_protocol_event_response = requests.post(
            url_for("api.sample_new_sample_protocol_event", _external=True),
            headers=get_internal_api_header(tokenuser),
            json={
                "event" : values["event"],
                "protocol_id": values["protocol_id"],
                "sample_id": sample_response.json()["content"]["id"]            },
        )

        if new_protocol_event_response.status_code == 200:

            try:
                disposal_event_values = new_sample_disposal_event_schema.load(
                    {
                        "sample_id": sample_response.json()["content"]["id"],
                        "reason": values["reason"],
                    }
                )
            except ValidationError as err:
                return validation_error_response(err)

            new_disposal_event = SampleDisposalEvent(**disposal_event_values)
            new_disposal_event.author_id = tokenuser.id

            try:

                db.session.add(new_disposal_event)
                db.session.commit()
                db.session.flush()

                sample = Sample.query.filter_by(
                    uuid=sample_response.json()["content"]["uuid"]
                ).first()

                if new_disposal_event.reason in ["DES", "FAI"]:
                    sample.status = "DES"
                elif new_disposal_event.reason == "TRA":
                    sample.status = "TRA"
                elif new_disposal_event.reason == "UNA":
                    sample.status = "MIS"
                else:
                    sample.status = "UNU"

                db.session.add(sample)
                db.session.commit()

                return success_with_content_response(
                    basic_sample_disposal_event_schema.dump(new_disposal_event)
                )

            except Exception as err:
                return transaction_error_response(err)

        else:
            return new_protocol_event_response.content
