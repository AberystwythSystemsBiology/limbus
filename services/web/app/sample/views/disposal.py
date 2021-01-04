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
from ...database import SampleDisposalProtocol

from ...consent.views import BasicConsentFormQuestionSchema, BasicConsentFormTemplateSchema

from ..enums import DisposalInstruction

import marshmallow_sqlalchemy as masql
from marshmallow_enum import EnumField

class BasicSampleDisposalSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleDisposalProtocol

    id = masql.auto_field()
    instruction = EnumField(DisposalInstruction)
    comments = masql.auto_field()
    disposal_date = masql.auto_field()


basic_disposal_schema = BasicSampleDisposalSchema()


class NewSampleDisposalSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleDisposalProtocol

    instruction = EnumField(DisposalInstruction)
    comments = masql.auto_field()
    disposal_date = masql.auto_field(allow_none=True)


new_sample_disposal_schema = NewSampleDisposalSchema()


