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

from ...extensions import ma
from ...database import SampleReview
from ...auth.views import BasicUserAccountSchema
from ...event.views import NewEventSchema, EventSchema

from ..enums import SampleQuality, ReviewResult, ReviewType

import marshmallow_sqlalchemy as masql
from marshmallow_enum import EnumField


class SampleReviewSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleReview

    id = masql.auto_field()
    uuid = masql.auto_field()
    quality = EnumField(SampleQuality, by_value=True)
    review_type = EnumField(ReviewType, by_value=True)
    result = EnumField(ReviewResult, by_value=True)
    event = ma.Nested(EventSchema)

    _links = ma.Hyperlinks(
        {
            "edit": ma.URLFor(
                "sample.edit_review", uuid="<uuid>", _external=True
            ),
            "remove": ma.URLFor(
                "sample.remove_review", uuid="<uuid>", _external=True
            ),
        }
    )


sample_review_schema = SampleReviewSchema()
sample_reviews_schema = SampleReviewSchema(many=True)


class NewSampleReviewSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleReview

    review_type = EnumField(ReviewType)
    result = EnumField(ReviewResult)
    sample_id = masql.auto_field()
    quality = EnumField(SampleQuality)
    event = ma.Nested(NewEventSchema)


new_sample_review_schema = NewSampleReviewSchema()
