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

from ...extensions import ma
from ...database import Donor, DonorProtocolEvent
from ..enums import RaceTypes, BiologicalSexTypes, DonorStatusTypes

from sqlalchemy_continuum import version_class, parent_class
from ...extensions import ma
import marshmallow_sqlalchemy as masql
from marshmallow import fields
from marshmallow_enum import EnumField

from ...auth.views import BasicUserAccountSchema, UserAccountSearchSchema
from ..enums import BiologicalSexTypes, DonorStatusTypes, RaceTypes
from ...sample.enums import Colour
from ...sample.views import (
    BasicSampleSchema,
    ConsentSchema,
    SampleSchema,
    BasicConsentSchema,
)

from .diagnosis import DonorDiagnosisEventSchema
from ...event.views import NewEventSchema, EventSchema
from ...protocol.views import BasicProtocolTemplateSchema


class DonorSearchSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Donor

    id = masql.auto_field()
    uuid = masql.auto_field()
    sex = EnumField(BiologicalSexTypes)  # , by_value=True)
    status = EnumField(DonorStatusTypes)  # , by_value=True)
    race = EnumField(RaceTypes)  # , by_value=True)
    colour = EnumField(Colour)  # , by_value=True)
    enrollment_site_id = masql.auto_field()

    consent_type = fields.String()
    not_consent_type = fields.String()
    diagnosis = fields.String()
    age_min = fields.Int()
    age_max = fields.Int()
    bmi_min = fields.Int()
    bmi_max = fields.Int()



class BasicDonorSchema(masql.SQLAlchemySchema):
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
    death_date = ma.Date()

    weight = masql.auto_field()
    height = masql.auto_field()

    diagnoses = ma.Nested(DonorDiagnosisEventSchema, many=True)

    race = EnumField(RaceTypes, by_value=True)

    author = ma.Nested(UserAccountSearchSchema)
    updater = ma.Nested(UserAccountSearchSchema)

    colour = EnumField(Colour, by_value=True)

    # consents = ma.Nested(ConsentSchema, many=True)
    consents = ma.Nested(BasicConsentSchema, many=True)
    samples_new = ma.Nested(BasicSampleSchema, many=True)
    # samples = ma.Nested(SampleSchema, many=True)

    created_on = ma.Date()
    updated_on = ma.Date()

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("donor.view", id="<id>", _external=True),
            "collection": ma.URLFor("donor.index", _external=True),
            "edit": ma.URLFor("donor.edit", id="<id>", _external=True),
            # "remove": ma.URLFor("donor.remove", id="<id>", _external=True),
            # "deep_remove": ma.URLFor("donor.deep_remove", id="<id>", _external=True),
            "new_sample": ma.URLFor(
                "donor.add_sample_step_one", id="<id>", _external=True
            ),
            "assign_diagnosis": ma.URLFor(
                "donor.new_diagnosis", id="<id>", _external=True
            ),
            "associate_sample": ma.URLFor(
                "donor.associate_sample", id="<id>", _external=True
            ),
        }
    )


basic_donor_schema = BasicDonorSchema()
basic_donors_schema = BasicDonorSchema(many=True)


class DonorSchema(masql.SQLAlchemySchema):
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
    death_date = ma.Date()

    weight = masql.auto_field()
    height = masql.auto_field()

    diagnoses = ma.Nested(DonorDiagnosisEventSchema, many=True)

    race = EnumField(RaceTypes, by_value=True)

    # author = ma.Nested(BasicUserAccountSchema)
    # updater = ma.Nested(BasicUserAccountSchema)
    author = ma.Nested(UserAccountSearchSchema)
    updater = ma.Nested(UserAccountSearchSchema)

    colour = EnumField(Colour, by_value=True)

    consents = ma.Nested(ConsentSchema, many=True)
    # samples = ma.Nested(BasicSampleSchema, many=True)
    samples = ma.Nested(SampleSchema, many=True)

    created_on = ma.Date()
    updated_on = ma.Date()

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("donor.view", id="<id>", _external=True),
            "collection": ma.URLFor("donor.index", _external=True),
            "edit": ma.URLFor("donor.edit", id="<id>", _external=True),
            "remove": ma.URLFor("donor.remove", id="<id>", _external=True),
            "deep_remove": ma.URLFor("donor.deep_remove", id="<id>", _external=True),
            "new_sample": ma.URLFor(
                "donor.add_sample_step_one", id="<id>", _external=True
            ),
            "assign_diagnosis": ma.URLFor(
                "donor.new_diagnosis", id="<id>", _external=True
            ),
            "associate_sample": ma.URLFor(
                "donor.associate_sample", id="<id>", _external=True
            ),
        }
    )


donor_schema = DonorSchema()
donors_schema = DonorSchema(many=True)


class NewDonorSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Donor

    id = masql.auto_field(default=None)
    dob = ma.Date()
    sex = EnumField(BiologicalSexTypes)
    status = EnumField(DonorStatusTypes)
    death_date = ma.Date(allow_none=True)
    colour = EnumField(Colour)
    mpn = masql.auto_field()
    enrollment_site_id = masql.auto_field()
    registration_date = masql.auto_field()

    weight = masql.auto_field()
    height = masql.auto_field()

    race = EnumField(RaceTypes, by_value=False)


new_donor_schema = NewDonorSchema()


class EditDonorSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Donor

    id = masql.auto_field(default=None, allow_none=True)
    dob = ma.Date(allow_none=True)
    sex = EnumField(BiologicalSexTypes, allow_none=True)
    status = EnumField(DonorStatusTypes, allow_none=True)
    death_date = ma.Date(allow_none=True)
    colour = EnumField(Colour, allow_none=True)
    mpn = masql.auto_field(allow_none=True)
    enrollment_site_id = masql.auto_field()
    registration_date = masql.auto_field()

    weight = masql.auto_field(allow_none=True)
    height = masql.auto_field(allow_none=True)

    race = EnumField(RaceTypes, allow_none=True)


edit_donor_schema = EditDonorSchema()


class NewDonorProtocolEventSchema(masql.SQLAlchemySchema):
    class Meta:
        model = DonorProtocolEvent

    is_locked = masql.auto_field()
    donor_id = masql.auto_field()
    reference_id = masql.auto_field()
    protocol_id = masql.auto_field()
    event = ma.Nested(NewEventSchema())


new_donor_protocol_event_schema = NewDonorProtocolEventSchema()


class DonorProtocolEventInfoSchema(masql.SQLAlchemySchema):
    class Meta:
        model = DonorProtocolEvent

    is_locked = masql.auto_field()
    uuid = masql.auto_field()
    id = masql.auto_field()
    donor_id = masql.auto_field()
    reference_id = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema)
    event = ma.Nested(EventSchema)
    created_on = ma.Date()

    protocol = ma.Nested(BasicProtocolTemplateSchema)

    _links = ma.Hyperlinks(
        {
            "edit": ma.URLFor(
                "donor.edit_protocol_event", uuid="<uuid>", _external=True
            ),
            "remove": ma.URLFor(
                "donor.remove_protocol_event", uuid="<uuid>", _external=True
            ),
        }
    )


donor_protocol_event_info_schema = DonorProtocolEventInfoSchema()
donor_protocol_events_info_schema = DonorProtocolEventInfoSchema(many=True)
