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
from ...database import SampleDisposal, SampleDisposalEvent

from ...consent.views import (
    BasicConsentFormQuestionSchema,
    BasicConsentFormTemplateSchema,
)

from ..enums import DisposalInstruction, DisposalReason
from ...event.views import NewEventSchema, EventSchema

import marshmallow_sqlalchemy as masql
from marshmallow_enum import EnumField


class NewSampleDiposalEventSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleDisposalEvent

    reason = EnumField(DisposalReason)
    event = ma.Nested(NewEventSchema)
    sample_id = masql.auto_field()
    protocol_event_id = masql.auto_field()


new_sample_disposal_event_schema = NewSampleDiposalEventSchema()


class BasicSampleDiposalEventSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleDisposalEvent

    id = masql.auto_field()
    event = ma.Nested(NewEventSchema)
    reason = EnumField(DisposalReason)
    sample_id = masql.auto_field()


basic_sample_disposal_event_schema = BasicSampleDiposalEventSchema()


class BasicSampleDisposalSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleDisposal

    id = masql.auto_field()
    #sample_id = masql.auto_field()
    instruction = EnumField(DisposalInstruction)
    comments = masql.auto_field()
    disposal_date = masql.auto_field()


basic_disposal_schema = BasicSampleDisposalSchema()


class NewSampleDisposalSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleDisposal

    sample_id = masql.auto_field()
    instruction = EnumField(DisposalInstruction)
    comments = masql.auto_field()
    disposal_date = masql.auto_field(allow_none=True)
    review_event_id = masql.auto_field(allow_none=True)


new_sample_disposal_schema = NewSampleDisposalSchema()

# TODO view on details for sample disposal