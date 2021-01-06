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
from ...database import SampleProtocolEvent
from ...auth.views import BasicUserAccountSchema
from ...protocol.views import BasicProtocolTemplateSchema

import marshmallow_sqlalchemy as masql

class NewSampleProtocolEventSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleProtocolEvent

    datetime = masql.auto_field()
    undertaken_by = masql.auto_field()
    comments = masql.auto_field()
    protocol_id = masql.auto_field()
    sample_id = masql.auto_field()
    


new_sample_protocol_event_schema = NewSampleProtocolEventSchema()


class SampleProtocolEventSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleProtocolEvent

    id = masql.auto_field()
    datetime = masql.auto_field(format="%d/%m/%Y")
    undertaken_by = masql.auto_field()
    comments = masql.auto_field()
    protocol = ma.Nested(BasicProtocolTemplateSchema)
    author = ma.Nested(BasicUserAccountSchema)
    created_on = ma.Date()


sample_protocol_event_schema = SampleProtocolEventSchema()


