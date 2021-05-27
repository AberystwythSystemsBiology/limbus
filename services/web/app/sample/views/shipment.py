# Copyright (C) 2021  Keiron O'Shea <keo7@aber.ac.uk>
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

from ...database import UserCart, SampleShipmentEvent, SampleShipmentEventToSample
from ...extensions import ma
import marshmallow_sqlalchemy as masql
from marshmallow_enum import EnumField

from ..views import BasicSampleSchema
from ...sample.views import SampleUUIDSchema
from ...auth.views import BasicUserAccountSchema
from ...misc.views import BasicSiteSchema

class SampleShipmentToSampleSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleShipmentEventToSample

    sample_id = masql.auto_field()
    sample = ma.Nested(SampleUUIDSchema, many=False)
    old_site = ma.Nested(BasicSiteSchema, many=False)

class SampleShipmentEventSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleShipmentEvent

    uuid = masql.auto_field()
    id = masql.auto_field()
    comments = masql.auto_field()
    datetime = masql.auto_field()
    author = ma.Nested(BasicUserAccountSchema, many=False)
    created_on = ma.Date()
    new_site = ma.Nested(BasicSiteSchema, many=False)

    involved_samples = ma.Nested(SampleShipmentToSampleSchema, many=True)



sample_shipment_event_schema = SampleShipmentEventSchema()
sample_shipment_events_schema = SampleShipmentEventSchema(many=True)

class BasicSampleShipmentEventSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleShipmentEvent
    
    uuid = masql.auto_field()
    id = masql.auto_field()
    datetime = masql.auto_field()
    author = ma.Nested(BasicUserAccountSchema, many=False)
    created_on = ma.Date()

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("sample.shipment_view_shipment", uuid="<uuid>", _external=True),
            "collection": ma.URLFor("sample.shipment_index", _external=True),
        }
    )

basic_sample_shipment_event_schema = BasicSampleShipmentEventSchema()
basic_sample_shipment_events_schema = BasicSampleShipmentEventSchema(many=True)




class NewSampleShipmentEventSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleShipmentEvent
    
    site_id = masql.auto_field(required=True)
    comments = masql.auto_field()
    datetime = masql.auto_field(required=True)

new_sample_shipment_event_schema = NewSampleShipmentEventSchema()


class NewUserCartSampleSchema(masql.SQLAlchemySchema):
    class Meta:
        model = UserCart

    sample_id = masql.auto_field()


new_cart_sample_schema = NewUserCartSampleSchema()


class UserCartSampleSchema(masql.SQLAlchemySchema):
    class Meta:
        model = UserCart

    sample = ma.Nested(BasicSampleSchema, many=False)
    author = ma.Nested(BasicUserAccountSchema, many=False)
    created_on = ma.Date()

user_cart_samples_schema = UserCartSampleSchema(many=True)