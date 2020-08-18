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
    SampleProtocolEvent,
)

from .views import (
    basic_samples_schema,
    new_consent_schema,
    consent_schema,
    new_consent_answer_schema,
    sample_protocol_event_schema,
    new_sample_protocol_event_schema,
    sample_protocol_event_schema,
    new_sample_schema,
)

from datetime import datetime


@api.route("/sample", methods=["GET"])
@token_required
def sample_home(tokenuser: UserAccount):
    return success_with_content_response(
        basic_samples_schema.dump(Sample.query.filter_by().all())
    )


@api.route("/sample/new_sample_protocol_event", methods=["POST"])
@token_required
def sample_new_sample_protocol_event(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        event_result = new_sample_protocol_event_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    new_event = SampleProtocolEvent(**event_result)
    new_event.author_id = tokenuser.id

    try:
        db.session.add(new_event)
        db.session.commit()
        db.session.flush()

        return success_with_content_response(
            sample_protocol_event_schema.dump(new_event)
        )

    except Exception as err:
        return transaction_error_response(err)

@api.route("/sample/new_sample_consent", methods=["POST"])
@token_required
def sample_new_sample_consent(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()


    try:
        consent_values = values["consent_data"]
        answer_values = values["answer_data"]

    except KeyError as err:
        return validation_error_response(err)


    try:
        consent_result = new_consent_schema.load(consent_values)
    except ValidationError as err:
        return validation_error_response(err)

    new_consent = SampleConsent(**consent_result)
    new_consent.author_id = tokenuser.id

    try:
        db.session.add(new_consent)
        db.session.commit()
        db.session.flush()
    except Exception as err:
        return transation_error_response(err)

    
    answers_list = []

    for answer in answer_values:
        try:
            answer_result = new_consent_answer_schema.load({
                "question_id": answer,
                "consent_id": new_consent.id
            })

            answers_list.append(answer_result)

        except ValidationError as err:
            return validation_error_response(err)
        
    for answer in answers_list:
        try:
            new_answer = SampleConsentAnswer(**answer)
            new_answer.author_id = tokenuser.id
            db.session.add(new_answer)
            db.session.commit()
        except Exception as err:
            return transaction_error_response(err)
    
    return success_with_content_response(
            consent_schema.dump(SampleConsent.query.filter_by(id=new_consent.id).first())
        )