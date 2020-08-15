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

from ..extensions import ma
import marshmallow_sqlalchemy as masql
from marshmallow import fields
from marshmallow_enum import EnumField

from ..auth.views import BasicUserAccountSchema

from ..database import (
    Sample,
    SampleConsent,
    SampleConsentAnswer,
    SampleProtocolEvent,
    SampleReview
)

from .enums import SampleType, SampleStatus, Colour, SampleSource, SampleQuality

class BasicSampleSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Sample

    id = masql.auto_field()

    author = ma.Nested(BasicUserAccountSchema)
    created_on = ma.Date()

basic_sample_schema = BasicSampleSchema()
basic_samples_schema = BasicSampleSchema(many=True)


class NewConsentSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleConsent

    identifier = masql.auto_field()
    comments = masql.auto_field()
    template_id = masql.auto_field()
    date_signed = masql.auto_field()


new_consent_schema = NewConsentSchema()


class ConsentSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleConsent

    id = masql.auto_field()
    identifier = masql.auto_field()
    comments = masql.auto_field()
    template_id = masql.auto_field()
    date_signed = masql.auto_field()
    author = ma.Nested(BasicUserAccountSchema)
    created_on = ma.Date()

consent_schema = ConsentSchema()

class NewConsentAnswerSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleConsentAnswer

    consent_id = masql.auto_field()
    question_id = masql.auto_field()


new_consent_answer_schema = NewConsentAnswerSchema()
new_consent_answers_schema = NewConsentAnswerSchema(many=True)


class NewSampleProtocolEventSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleProtocolEvent

    datetime = masql.auto_field()
    undertaken_by = masql.auto_field()
    comments = masql.auto_field()
    protocol_id = masql.auto_field()

new_sample_protocol_event_schema = masql.SQLAlchemySchema


class SampleProtocolEventSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleProtocolEvent

    id = masql.auto_field()
    datetime = masql.auto_field()
    undertaken_by = masql.auto_field()
    comments = masql.auto_field()
    protocol_id = masql.auto_field()
    author = ma.Nested(BasicUserAccountSchema)
    created_on = ma.Date()

sample_protocol_event_schema = SampleProtocolEventSchema()

class NewSampleSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Sample

    barcode = masql.auto_field()
    source = EnumField(SampleSource)
    type = EnumField(SampleType)
    status = EnumField(SampleStatus)
    colour = EnumField(Colour)
    comments = masql.auto_field()
    site_id = masql.auto_field()
    consent_id = masql.auto_field()
    collection_event_id = masql.auto_field()
    processing_event_id = masql.auto_field()

new_sample_schema = NewSampleSchema()

class NewSampleReviewSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleReview

    sample_id = masql.auto_field()
    conducted_by = masql.auto_field()
    datetime = masql.auto_field()
    quality = EnumField(SampleQuality)
    comments = masql.auto_field()

new_sample_review_schema = NewSampleReviewSchema()

