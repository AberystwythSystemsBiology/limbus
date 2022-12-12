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
    Donor,
)
import marshmallow_sqlalchemy as masql
from marshmallow_enum import EnumField
from marshmallow import fields
from ...auth.views import UserAccountSearchSchema
from ...misc.views import SiteNameSchema
from ...event.views import NewEventSchema
from ..enums import SampleShipmentStatusStatus

from ...donor.enums import BiologicalSexTypes, DonorStatusTypes, RaceTypes

# from ..enums import SampleBaseType, Colour, SampleSource, SampleStatus, BiohazardLevel
from ...database import DonorDiagnosisEvent
from ...donor.enums import CancerStage
from ...disease.api import retrieve_by_iri


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


class DoidInstance(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        return retrieve_by_iri(value)


class BasicDonorDiagnosisEventSchema(masql.SQLAlchemySchema):
    class Meta:
        model = DonorDiagnosisEvent

    diagnosis_date = ma.Date()
    comments = masql.auto_field()
    doid_ref = DoidInstance()
    stage = EnumField(CancerStage)


class DonorIndexSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Donor

    id = masql.auto_field()
    uuid = masql.auto_field()
    mpn = masql.auto_field()
    enrollment_site_id = masql.auto_field()
    dob = ma.Date()
    registration_date = ma.Date()
    sex = EnumField(BiologicalSexTypes, by_value=True)
    status = EnumField(DonorStatusTypes, by_value=True)
    weight = masql.auto_field()
    height = masql.auto_field()
    diagnoses = ma.Nested(BasicDonorDiagnosisEventSchema, many=True)


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
