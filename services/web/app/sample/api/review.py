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

from ..views import new_sample_review_schema, sample_review_schema, new_sample_disposal_schema

from ...database import db, Sample, SampleReview, SampleDisposal, UserAccount, Event
from sqlalchemy.sql import func


@api.route("/sample/new/review_disposal", methods=["POST"])
@token_required
def sample_new_sample_review_disposal(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    disposal_info = None
    if "disposal_info" in values:
        disposal_info = values.pop("disposal_info")

    sample = Sample.query.filter_by(id=values["sample_id"]).first_or_404()
    disposal_id = sample.disposal_id
    disposal_info["sample_id"] = sample.id

    try:
        sample_review_values = new_sample_review_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    if disposal_info:
        try:
            results = new_sample_disposal_schema.load(disposal_info)
        except ValidationError as err:
            return validation_error_response(err)

    new_event = Event(
        datetime=sample_review_values["event"]["datetime"],
        undertaken_by=sample_review_values["event"]["undertaken_by"],
        comments=sample_review_values["event"]["comments"],
        author_id=tokenuser.id,
    )

    try:
        db.session.add(new_event)
        db.session.flush()
        print("new_event.id: ", new_event.id)
    except Exception as err:
        return transaction_error_response(err)


    new_sample_review = SampleReview(
        result=sample_review_values["result"],
        review_type=sample_review_values["review_type"],
        sample_id=sample.id,
        quality=sample_review_values["quality"],
        author_id=tokenuser.id,
        event_id=new_event.id,
    )
    try:
        db.session.add(new_sample_review)
        db.session.flush()
        print("new_review.id: ", new_sample_review.id)
    except Exception as err:
        return transaction_error_response(err)


    if disposal_info:
        # Add new disposal instruction
        # Update if existing instruction hasn't been approved
        new_instruction = True
        if disposal_id:
            disposal_instruction = SampleDisposal.query.filter_by(id=disposal_id).\
                               first_or_404()
            if disposal_instruction:
                if not disposal_instruction.approval_event_id:
                    new_instruction = False

        if new_instruction:
            disposal_instruction = SampleDisposal(**disposal_info)
            disposal_instruction.review_event_id = new_sample_review.id
            disposal_instruction.author_id = tokenuser.id

        else:
            #for attr, value in disposal_info.items():
            #    setattr(disposal_instruction, attr, value)
            disposal_instruction.update(disposal_info)
            disposal_instruction.review_event_id = new_sample_review.id
            disposal_instruction.editor_id = tokenuser.id
            disposal_instruction.updated_on = func.now()

        try:
            db.session.add(disposal_instruction)
            db.session.flush()
            print("disposal_id: ", disposal_instruction.id)
        except Exception as err:
            return transaction_error_response(err)

        sample.disposal_id = disposal_instruction.id

        # TODO sample.status update!!

    try:
        db.session.add(sample)
        db.session.commit()

        return success_with_content_response(
            sample_review_schema.dump(new_sample_review)
        )
    except Exception as err:
        return transaction_error_response(err)


@api.route("/sample/new/review", methods=["POST"])
@token_required
def sample_new_sample_review(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        sample_review_values = new_sample_review_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    new_event = Event(
        datetime=sample_review_values["event"]["datetime"],
        undertaken_by=sample_review_values["event"]["undertaken_by"],
        comments=sample_review_values["event"]["comments"],
        author_id=tokenuser.id,
    )

    try:
        db.session.add(new_event)
        db.session.commit()
        db.session.flush()
    except Exception as err:
        return transaction_error_response(err)

    sample = Sample.query.filter_by(id=values["sample_id"]).first_or_404()

    new_sample_review = SampleReview(
        result=sample_review_values["result"],
        review_type=sample_review_values["review_type"],
        sample_id=sample.id,
        quality=sample_review_values["quality"],
        author_id=tokenuser.id,
        event_id=new_event.id,
    )

    try:
        db.session.add(new_sample_review)
        db.session.add(sample)
        db.session.commit()
        db.session.flush()

        return success_with_content_response(
            sample_review_schema.dump(new_sample_review)
        )
    except Exception as err:
        return transaction_error_response(err)
