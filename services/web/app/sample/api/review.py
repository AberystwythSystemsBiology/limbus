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

from ..views import new_sample_review_schema, sample_review_schema

from ...database import db, Sample, SampleReview, UserAccount, Event


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
