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
from ...misc import get_internal_api_header

from ..views import (
    new_consent_schema,
    consent_schema
)

from ...database import (
    db,
    SampleConsent,
    SampleConsentAnswer,
    UserAccount
)

@api.route("/sample/new/consent", methods=["POST"])
@token_required
def sample_new_sample_consent(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()
    
    errors = {}
    for key in ["identifier", "comments", "template_id", "date", "answers"]:
        if key not in values.keys():
            errors[key] = ["Not found."]

    if len(errors.keys()) > 0:
        return validation_error_response(errors)

    answers = values["answers"]
    values.pop("answers")


    try:
        consent_result = new_consent_schema.load(values)
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

    for answer in answers:
        try:
            answer_result = new_consent_answer_schema.load({"question_id": int(answer), "consent_id": new_consent.id})
        except ValidationError as err:
            return validation_error_response(err)

        new_answer = SampleConsentAnswer(**answer_result)
        new_answer.author_id = tokenuser.id
        
        try:
            db.session.add(new_answer)
            db.session.commit()
        except Exception as err:
            return transaction_error_response(err)

    return success_with_content_response(
        consent_schema.dump(SampleConsent.query.filter_by(id=new_consent.id).first())
    )
