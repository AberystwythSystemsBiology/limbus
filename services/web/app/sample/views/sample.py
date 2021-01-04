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

from ...database import Sample
from ...auth.views import BasicUserAccountSchema
from ...extensions import ma
from ..enums import (
    SampleBaseType,
    Colour,
    SampleSource,
    SampleStatus,
    BiohazardLevel,
    SampleStorageRequirement
)

from . import (
    SampleUUIDSchema,
    SampleTypeSchema,
    SampleProtocolEventSchema,
    BasicSampleDisposalSchema,
    ConsentSchema,
    SampleReviewSchema
)

from ...document.views import BasicDocumentSchema

import marshmallow_sqlalchemy as masql
from marshmallow import fields
from marshmallow_enum import EnumField


_links = ma.Hyperlinks(
        {
            "self": ma.URLFor("sample.view", uuid="<uuid>", _external=True),
            "collection": ma.URLFor("sample.index", _external=True),
            "webapp_query": ma.URLFor("sample.query", _external=True),
            "webapp_aliquot": ma.URLFor(
                "sample.aliquot_endpoint", uuid="<uuid>", _external=True
            ),
            "label": ma.URLFor("labels.sample_label", uuid="<uuid>", _external=True),
            "barcode_generation": ma.URLFor(
                "api.misc_generate_barcode", _external=True
            ),
        }
    )

class NewSampleSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Sample

    colour = EnumField(Colour)
    barcode = masql.auto_field()
    bioharzard_level = EnumField(BiohazardLevel)
    source = EnumField(SampleSource)
    base_type = EnumField(SampleBaseType)
    status = EnumField(SampleStatus)
    collection_event_id = masql.auto_field()
    quantity = masql.auto_field()
    site_id = masql.auto_field()
    consent_id = masql.auto_field()
    storage_requirement = EnumField(SampleStorageRequirement)



new_sample_schema = NewSampleSchema()

class BasicSampleSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Sample

    id = masql.auto_field()

basic_sample_schema = BasicSampleSchema()
basic_samples_schema = BasicSampleSchema(many=True)


class SampleSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Sample
    id = masql.auto_field()

sample_schema = SampleSchema()
