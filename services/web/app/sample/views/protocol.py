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
from ...auth.views import BasicUserAccountSchema, UserAccountSearchSchema
from ...protocol.views import BasicProtocolTemplateSchema
from ...event.views import EventSchema, NewEventSchema

import marshmallow_sqlalchemy as masql


class NewSampleProtocolEventSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleProtocolEvent

    is_locked = masql.auto_field()
    sample_id = masql.auto_field()
    reduced_quantity = masql.auto_field()
    event = ma.Nested(NewEventSchema())
    protocol_id = masql.auto_field()


new_sample_protocol_event_schema = NewSampleProtocolEventSchema()


class SampleProtocolEventSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleProtocolEvent

    is_locked = masql.auto_field()
    uuid = masql.auto_field()
    id = masql.auto_field()
    reduced_quantity = masql.auto_field()
    #author = ma.Nested(BasicUserAccountSchema)
    author = ma.Nested(UserAccountSearchSchema)
    event = ma.Nested(EventSchema)
    created_on = ma.Date()

    protocol = ma.Nested(BasicProtocolTemplateSchema)

    _links = ma.Hyperlinks(
        {
            "edit": ma.URLFor(
                "sample.edit_protocol_event", uuid="<uuid>", _external=True
            ),
            "remove": ma.URLFor(
                "sample.remove_protocol_event", uuid="<uuid>", _external=True
            ),
        }
    )

sample_protocol_event_schema = SampleProtocolEventSchema()
sample_protocol_events_schema = SampleProtocolEventSchema(many=True)
