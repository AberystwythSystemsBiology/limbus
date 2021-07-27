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

from ...database import UserCart, SampleShipment, SampleShipmentToSample
from ...extensions import ma
import marshmallow_sqlalchemy as masql
from marshmallow_enum import EnumField

from ..views import BasicSampleSchema
from ...storage.views import BasicSampleRackSchema
from ...sample.views import SampleUUIDSchema
from ...auth.views import BasicUserAccountSchema
from ...misc.views import BasicSiteSchema
from ...event.views import NewEventSchema, EventSchema

from ..enums import CartSampleStorageType


class SampleShipmentToSampleSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleShipmentToSample

    sample_id = masql.auto_field()
    sample = ma.Nested(SampleUUIDSchema, many=False)
    old_site = ma.Nested(BasicSiteSchema, many=False)


class SampleShipmentSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleShipment

    uuid = masql.auto_field()
    id = masql.auto_field()
    author = ma.Nested(BasicUserAccountSchema, many=False)
    created_on = ma.Date()
    new_site = ma.Nested(BasicSiteSchema, many=False)

    involved_samples = ma.Nested(SampleShipmentToSampleSchema, many=True)


sample_shipment_schema = SampleShipmentSchema()
sample_shipments_schema = SampleShipmentSchema(many=True)


class BasicSampleShipmentSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleShipment

    uuid = masql.auto_field()
    id = masql.auto_field()
    author = ma.Nested(BasicUserAccountSchema, many=False)
    created_on = ma.Date()

    event = ma.Nested(EventSchema())

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor(
                "sample.shipment_view_shipment", uuid="<uuid>", _external=True
            ),
            "collection": ma.URLFor("sample.shipment_index", _external=True),
        }
    )


basic_sample_shipment_schema = BasicSampleShipmentSchema()
basic_sample_shipments_schema = BasicSampleShipmentSchema(many=True)


class NewSampleShipmentSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleShipment

    site_id = masql.auto_field(required=True)
    event = ma.Nested(NewEventSchema())



new_sample_shipment_schema = NewSampleShipmentSchema()


class NewUserCartSampleSchema(masql.SQLAlchemySchema):
    class Meta:
        model = UserCart

    sample_id = masql.auto_field()


new_cart_sample_schema = NewUserCartSampleSchema()


class UserCartSampleSchema(masql.SQLAlchemySchema):
    class Meta:
        model = UserCart

    sample = ma.Nested(BasicSampleSchema, many=False)
    rack = ma.Nested(BasicSampleRackSchema, many=False)
    storage_type = EnumField(CartSampleStorageType)
    author = ma.Nested(BasicUserAccountSchema, many=False)
    created_on = ma.Date()


user_cart_samples_schema = UserCartSampleSchema(many=True)
