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

from flask import request, abort

from marshmallow import ValidationError

from ..api import api
from ..api.responses import *
from ..decorators import token_required
from ..database import (
    db,
    UserAccount,
    Sample,
    SampleConsent,
    SampleConsentAnswer,
    SampleProtocolEvent
)

from .views import (
    basic_samples_schema,
    new_consent_schema,
    consent_schema,
    new_consent_answer_schema,
    new_sample_protocol_event_schema,
    sample_protocol_event_schema,
    new_sample_schema

)

import datetime


@api.route("/sample", methods=["GET"])
@token_required
def sample_home(tokenuser: UserAccount):
    return success_with_content_response(
        basic_samples_schema.dump(Sample.query.filter_by().all())
    )

@api.route("/sample/add", methods=["POST"])
@token_required
def sample_add_sample(tokenuser: UserAccount):

    def _add_consent(template_id: int, consent_data: dict):
        new_consent_data = {
            "template_id": int(template_id),
            "identifier": consent_data["consent_id"],
            "date_signed": consent_data["date_signed"],
            "comments": consent_data["comments"]
        }
        try:
            result = new_consent_schema.load(new_consent_data)
        except ValidationError as err:
            return validation_error_response(err)

        new_consent = SampleConsent(**result)
        new_consent.author_id = tokenuser.id

        try:
            db.session.add(new_consent)
            db.session.flush()
        except Exception as err:
            return transaction_error_response(err)

        for checked in consent_data["checked"]:
            try:
                new_answer_data = {
                    "question_id": int(checked),
                    "consent_id": new_consent.id

                }
                result = new_consent_answer_schema.load(new_answer_data)
            except ValidationError as err:
                return validation_error_response(err)

            new_answer = SampleConsentAnswer(**result)
            new_answer.author_id = tokenuser.id

            try:
                db.session.add(new_answer)
                db.session.flush()
            except Exception as err:
                return transaction_error_response(err)

        db.session.commit()

        return success_with_content_response(
            consent_schema.dump(new_consent)
        )

    def _add_processing_information(processing_data: dict):
        add_processing_data = {
            "datetime": datetime.strptime(
                "%s %s" % (
                    processing_data["processing_date"],
                    processing_data["processing_time"]
                ), "%Y/%m/%d %H:%M:%S"),
            "undertaken_by": processing_data["undertaken_by"],
            "comments": processing_data["comments"],
            "protocol_id": int(processing_data["processing_protocol_id"])
        }
        try:
            result = new_sample_protocol_event_schema.load(add_processing_data)
        except ValidationError as err:
            return validation_error_response(err)

        new_processing_event = SampleProtocolEvent(**result)
        new_processing_event.author_id = tokenuser.id

        try:
            db.session.add(new_processing_event)
            db.session.flush()
        except Exception as err:
            return transaction_error_response(err)

        db.session.flush()
        return success_with_content_response(
            sample_protocol_event_schema.dump(new_processing_event)
        )

    def _add_collection(collection_data):
        add_processing_data = {
            "datetime": datetime.strptime(
                "%s %s" % (
                    collection_data["collection_data"],
                    collection_data["collection_data"]
                ), "%Y/%m/%d %H:%M:%S"),
            "undertaken_by": collection_data["collected_by"],
            "comments": None,
            "protocol_id": int(collection_data["collection_protocol_id"])
        }

        try:
            result = new_sample_protocol_event_schema.load(add_processing_data)
        except ValidationError as err:
            return validation_error_response(err)

        new_processing_event = SampleProtocolEvent(**result)
        new_processing_event.author_id = tokenuser.id

        try:
            db.session.add(new_processing_event)
            db.session.flush()
        except Exception as err:
            return transaction_error_response(err)

        db.session.flush()

        return success_with_content_response(
            sample_protocol_event_schema.dump(new_processing_event)
        )

    def _add_sample_information(collection_data, site_id, consent_id,):
        pass


    values = request.get_json()

    if not values:
        return no_values_response()

    steps = [
        "add_processing_information", # Done
        "add_sample_information",
        "add_sample_review",
        "add_collection_consent_and_barcode",
        "add_digital_consent_form",  # Done
        "add_final_details"
    ]

    for step in steps:
        if step not in values.keys():
            print(step)
            return {"success": False, "message": "Missing %s" % (step)}, 400, {"ContentType": "application/json"}


    collection_response, status_code, response_type = _add_consent(
        values["add_collection_consent_and_barcode"]["consent_form_id"],
        values["add_digital_consent_form"]
    )

    if status_code != 200:
        return collection_response, status_code, response_type

    processing_response, status_code, response_type = _add_processing_information(
        values["add_processing_information"]
    )

    if status_code != 200:
        return processing_response, status_code, response_type

    collection_response, status_code, response_type = _add_collection(
        values["add_collection_consent_and_barcode"]
    )

    if status_code != 200:
        return collection_response, status_code, response_type


