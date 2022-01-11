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

from ...database import (
    UserCart,
    SampleShipment,
    SampleShipmentToSample,
    SampleShipmentStatus,
)
from ...extensions import ma
import marshmallow_sqlalchemy as masql
from marshmallow_enum import EnumField

from ..views import BasicSampleSchema, BasicDisposalSampleSchema
from ...storage.views import BasicSampleRackSchema
from ...sample.views import SampleUUIDSchema, SampleProtocolEventSchema
from ...auth.views import BasicUserAccountSchema, UserAccountSearchSchema
from ...misc.views import BasicSiteSchema, BasicAddressSchema
from ...event.views import NewEventSchema, EventSchema

from ..enums import CartSampleStorageType, SampleShipmentStatusStatus


class SampleShipmentToSampleUUIDSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleShipmentToSample

    sample_id = masql.auto_field()
    sample = ma.Nested(SampleUUIDSchema, many=False)
    old_site = ma.Nested(BasicSiteSchema, many=False)


class SampleShipmentToSampleSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleShipmentToSample

    sample_id = masql.auto_field()
    sample = ma.Nested(BasicSampleSchema, many=False)
    old_site = ma.Nested(BasicSiteSchema, many=False)
    transfer_protocol = ma.Nested(SampleProtocolEventSchema)


class SampleShipmentSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleShipment

    uuid = masql.auto_field()
    id = masql.auto_field()
    is_locked = masql.auto_field()

    author = ma.Nested(UserAccountSearchSchema, many=False)
    created_on = ma.Date()
    new_site = ma.Nested(BasicSiteSchema, many=False)
    to_address = ma.Nested(BasicAddressSchema, many=False)

    # involved_samples = ma.Nested(SampleShipmentToSampleUUIDSchema, many=True)
    involved_samples = ma.Nested(SampleShipmentToSampleSchema, many=True)
    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor(
                "sample.shipment_view_shipment", uuid="<uuid>", _external=True
            ),
            "collection": ma.URLFor("sample.shipment_index", _external=True),
        }
    )


sample_shipment_schema = SampleShipmentSchema()
sample_shipments_schema = SampleShipmentSchema(many=True)


class SampleShipmentStatusSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleShipmentStatus

    status = EnumField(SampleShipmentStatusStatus, by_value=True)
    datetime = masql.auto_field()
    comments = masql.auto_field()
    courier = masql.auto_field()
    tracking_number = masql.auto_field()
    shipment = ma.Nested(SampleShipmentSchema, many=False)


sample_shipment_status_schema = SampleShipmentStatusSchema()
sample_shipments_status_schema = SampleShipmentStatusSchema(many=True)


class NewSampleShipmentStatusSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleShipmentStatus

    shipment_id = masql.auto_field()
    status = EnumField(SampleShipmentStatusStatus, by_value=False)
    datetime = masql.auto_field()
    comments = masql.auto_field()
    courier = masql.auto_field()
    tracking_number = masql.auto_field()


new_sample_shipment_status_schema = NewSampleShipmentStatusSchema()


class NewSampleShipmentSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleShipment

    site_id = masql.auto_field(required=True)
    address_id = masql.auto_field(required=True)
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

    # sample = ma.Nested(BasicSampleSchema, many=False)
    sample = ma.Nested(BasicDisposalSampleSchema, many=False)
    rack = ma.Nested(BasicSampleRackSchema, many=False)
    selected = masql.auto_field()
    storage_type = EnumField(CartSampleStorageType)
    author = ma.Nested(UserAccountSearchSchema, many=False)
    created_on = ma.Date()


user_cart_samples_schema = UserCartSampleSchema(many=True)
