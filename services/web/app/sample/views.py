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

from ..extensions import ma
import marshmallow_sqlalchemy as masql
from marshmallow import fields
from marshmallow_enum import EnumField

from ..auth.views import BasicUserAccountSchema
from ..consent.views import (
    BasicConsentFormQuestionSchema,
    BasicConsentFormTemplateSchema,
)
from ..document.views import BasicDocumentSchema
from ..protocol.views import BasicProtocolTemplateSchema

from ..database import (
    Sample,
    SampleConsent,
    SampleConsentAnswer,
    SampleProtocolEvent,
    SampleReview,
    SampleToType,
    SampleDisposal,
    SampleDocument
)

from .enums import (
    SampleType,
    SampleStatus,
    FluidContainer,
    Colour,
    SampleSource,
    SampleQuality,
    MolecularSampleType,
    TissueSampleType,
    BiohazardLevel,
    DisposalInstruction,
    CellSampleType,
    FixationType,
    FluidSampleType,
    CellContainer,
    FluidSampleType,
    SampleType,
)


import requests
from flask import url_for
from ..misc import get_internal_api_header


class NewConsentSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleConsent

    identifier = masql.auto_field()
    comments = masql.auto_field()
    template_id = masql.auto_field()
    date_signed = masql.auto_field()


new_consent_schema = NewConsentSchema()


class ConsentSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleConsent

    id = masql.auto_field()
    identifier = masql.auto_field()
    comments = masql.auto_field()
    template = ma.Nested(BasicConsentFormTemplateSchema, many=False)
    author = ma.Nested(BasicUserAccountSchema, many=False)
    created_on = ma.Date()
    answers = ma.Nested(BasicConsentFormQuestionSchema, many=True)


consent_schema = ConsentSchema()


class NewConsentAnswerSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleConsentAnswer

    consent_id = masql.auto_field()
    question_id = masql.auto_field()


new_consent_answer_schema = NewConsentAnswerSchema()
new_consent_answers_schema = NewConsentAnswerSchema(many=True)


class BasicSampleDisposalSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleDisposal

    id = masql.auto_field()
    instruction = EnumField(DisposalInstruction)
    comments = masql.auto_field()
    disposal_date = masql.auto_field()


basic_disposal_schema = BasicSampleDisposalSchema()

class SampleDocumentSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleDocument
    
    sample_id = masql.auto_field()
    document_id = masql.auto_field()

sample_document_schema = SampleDocumentSchema()

class NewDocumentToSampleSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleDocument

    sample_id = masql.auto_field()
    document_id = masql.auto_field()

new_document_to_sample_schema = NewDocumentToSampleSchema()

class NewSampleDisposalSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleDisposal

    instruction = EnumField(DisposalInstruction)
    comments = masql.auto_field()
    disposal_date = masql.auto_field(allow_none=True)


new_sample_disposal_schema = NewSampleDisposalSchema()


class NewSampleProtocolEventSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleProtocolEvent

    datetime = masql.auto_field()
    undertaken_by = masql.auto_field()
    comments = masql.auto_field()

    protocol_id = masql.auto_field()


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


class SampleTypeSchema(ma.SQLAlchemySchema):
    class Meta:
        model = SampleToType

    id = masql.auto_field()

    flui_type = EnumField(FluidSampleType)
    mole_type = EnumField(MolecularSampleType)
    cell_type = EnumField(CellSampleType)
    tiss_type = EnumField(TissueSampleType)

    author = ma.Nested(BasicUserAccountSchema)
    container_id = masql.auto_field()


sample_type_schema = SampleTypeSchema()


class NewFluidSampleSchema(ma.Schema):
    fluid_sample_type = EnumField(FluidSampleType)
    fluid_container = EnumField(FluidContainer)


new_fluid_sample_schema = NewFluidSampleSchema()


class NewCellSampleSchema(ma.Schema):
    cell_sample_type = EnumField(CellSampleType)
    tissue_sample_type = EnumField(TissueSampleType)
    fixation_type = EnumField(FixationType)
    cell_container = EnumField(CellContainer)


new_cell_sample_schema = NewCellSampleSchema()


class NewMolecularSampleSchema(ma.Schema):
    molecular_sample_type = EnumField(FluidSampleType)
    fluid_container = EnumField(MolecularSampleType)


new_molecular_sample_schema = NewMolecularSampleSchema()


class NewSampleSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Sample

    barcode = masql.auto_field(allow_none=True)
    source = EnumField(SampleSource)
    type = EnumField(SampleType)
    status = EnumField(SampleStatus)
    colour = EnumField(Colour)
    biohazard_level = EnumField(BiohazardLevel)
    comments = masql.auto_field()
    site_id = masql.auto_field(allow_none=True)
    quantity = masql.auto_field()
    disposal_id = masql.auto_field(allow_none=True)
    sample_to_type_id = masql.auto_field()
    consent_id = masql.auto_field()
    collection_event_id = masql.auto_field(allow_none=True)
    processing_event_id = masql.auto_field(allow_none=True)


new_sample_schema = NewSampleSchema()


class SampleSearchSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Sample

    barcode = masql.auto_field()
    colour = masql.auto_field()
    type = masql.auto_field()
    biohazard_level = masql.auto_field()
    source = masql.auto_field()
    status = masql.auto_field()


class NewSampleReviewSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleReview

    sample_id = masql.auto_field()
    conducted_by = masql.auto_field()
    datetime = masql.auto_field()
    quality = EnumField(SampleQuality)
    comments = masql.auto_field()


new_sample_review_schema = NewSampleReviewSchema()


class SampleUUIDSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Sample

    uuid = masql.auto_field(required=False)

    _links = ma.Hyperlinks(
        {"self": ma.URLFor("sample.view", uuid="<uuid>", _external=True)}
    )

class SampleToTypeSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleToType
    
    flui_type = EnumField(FluidSampleType, by_value=True)
    mole_type = EnumField(MolecularSampleType, by_value=True)
    cell_type = EnumField(CellSampleType, by_value=True)
    tiss_type = EnumField(TissueSampleType, by_value=True)

class BasicSampleSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Sample

    id = masql.auto_field()
    uuid = masql.auto_field(required=False)
    type = EnumField(SampleType, by_value=True)
    quantity = masql.auto_field()
    remaining_quantity = masql.auto_field()
    status = EnumField(SampleType, by_value=True)

    colour = EnumField(Colour, by_value=True)
    source = EnumField(SampleSource, by_value=True)
    created_on = ma.Date()
    parent = ma.Nested(SampleUUIDSchema, many=False)

    sample_type_information = ma.Nested(SampleToTypeSchema)

    barcode = masql.auto_field()
    collection_information = ma.Nested(SampleProtocolEventSchema, many=False)

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("sample.view", uuid="<uuid>", _external=True),
            "collection": ma.URLFor("sample.index", _external=True),
            "qr_code": ma.URLFor("sample.view_barcode", uuid="<uuid>", t="qrcode", _external=True)
        }
    )


basic_sample_schema = BasicSampleSchema()
basic_samples_schema = BasicSampleSchema(many=True)


class SampleSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Sample

    id = masql.auto_field()

    uuid = masql.auto_field()
    type = EnumField(SampleType, by_value=True)
    is_locked = masql.auto_field()
    # Need to get container stuff.

    sample_type_information = None

    quantity = masql.auto_field()
    remaining_quantity = masql.auto_field()
    comments = masql.auto_field()
    barcode = masql.auto_field()

    colour = EnumField(Colour, by_value=True)
    source = EnumField(SampleSource, by_value=True)
    biohazard_level = EnumField(BiohazardLevel, by_value=True)
    status = EnumField(SampleSource, by_value=True)
    site_id = masql.auto_field(allow_none=True)
    author = ma.Nested(BasicUserAccountSchema, many=False)
    processing_information = ma.Nested(SampleProtocolEventSchema, many=False, allow_none=True)
    collection_information = ma.Nested(SampleProtocolEventSchema, many=False, allow_none=True)
    disposal_information = ma.Nested(BasicSampleDisposalSchema, many=False, allow_none=True)
    consent_information = ma.Nested(ConsentSchema, many=False)

    documents = ma.Nested(BasicDocumentSchema, many=True, allow_none=True)

    parent = ma.Nested(BasicSampleSchema, many=False, allow_none=True)
    subsamples = ma.Nested(BasicSampleSchema, many=True, allow_none=True)

    created_on = ma.Date()

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("sample.view", uuid="<uuid>", _external=True),
            "collection": ma.URLFor("sample.index", _external=True),
            "webapp_query": ma.URLFor("sample.query", _external=True),
            "webapp_aliquot": ma.URLFor(
                "sample.aliquot_endpoint", uuid="<uuid>", _external=True
            )

        }
    )


sample_schema = SampleSchema()
