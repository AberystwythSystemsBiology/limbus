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
from ...database import (
    Sample,
    SampleShipmentStatus,
    SampleShipment,
    SampleShipmentToSample,
)
import marshmallow_sqlalchemy as masql
from marshmallow_enum import EnumField

from ...auth.views import UserAccountSearchSchema
from ...misc.views import SiteNameSchema
from ...event.views import NewEventSchema
from ..enums import SampleShipmentStatusStatus


class SampleUUIDSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Sample

    uuid = masql.auto_field(required=False)

    _links = ma.Hyperlinks(
        {"self": ma.URLFor("sample.view", uuid="<uuid>", _external=True)}
    )


class BasicSampleShipmentStatusSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleShipmentStatus

    status = EnumField(SampleShipmentStatusStatus, by_value=True)
    datetime = masql.auto_field()
    comments = masql.auto_field()
    tracking_number = masql.auto_field()


basic_sample_shipment_status_schema = BasicSampleShipmentStatusSchema()
basic_sample_shipments_status_schema = BasicSampleShipmentStatusSchema(many=True)


class BasicSampleShipmentSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleShipment

    uuid = masql.auto_field()
    id = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    new_site = ma.Nested(SiteNameSchema, many=False)
    created_on = ma.Date()
    shipment_status = ma.Nested(BasicSampleShipmentStatusSchema)  # , many=False)
    event = ma.Nested(NewEventSchema())

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


class SampleShipmentToSampleInfoSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleShipmentToSample

    shipment = ma.Nested(BasicSampleShipmentSchema, many=False)
    old_site = ma.Nested(SiteNameSchema, many=False)


from .filter import *
from .consent import *

# from .disposal import *
from .document import *
from .filter import *
from .protocol import *
from .review import *
from .disposal import *
from .type import *
from .storage import *
from .sample import *
from .attribue import *
from .shipment import *
