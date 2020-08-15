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
    SampleConsentAnswer
)

from .views import (
    basic_samples_schema,
    new_consent_schema,
    consent_schema,
    new_consent_answer_schema,

)



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

    values = request.get_json()

    if not values:
        return no_values_response()

    steps = [
        "add_processing_information",
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


    response, status_code, response_type = _add_consent(
        values["add_collection_consent_and_barcode"]["consent_form_id"],
        values["add_digital_consent_form"]
    )

    if status_code != 200:
        return response, status_code, response_type


