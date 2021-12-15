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

from ...database import Sample, SampleProtocolEvent, SubSampleToSample
from ...event.views import EventSchema
from ...protocol.views import BasicProtocolTemplateSchema
from ...auth.views import BasicUserAccountSchema, UserAccountSearchSchema
from ...extensions import ma
from ..enums import SampleBaseType, Colour, SampleSource, SampleStatus, BiohazardLevel


from . import (
    SampleUUIDSchema,
    SampleTypeSchema,
    BasicSampleDisposalSchema,
    BasicConsentSchema,
    ConsentSchema,
    EntityToStorageSchema,
    BasicSampleDiposalEventSchema,
    SampleShipmentToSampleInfoSchema,
)

from ...document.views import BasicDocumentSchema
from ...attribute.views import AttributeDataSchema
from ..views import SampleProtocolEventSchema, SampleReviewSchema#, SampleProtocolEventViewSchema

import marshmallow_sqlalchemy as masql
from marshmallow import fields
from marshmallow_enum import EnumField


class NewSampleSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Sample

    barcode = masql.auto_field()
    source = EnumField(SampleSource)
    base_type = EnumField(SampleBaseType)
    status = EnumField(SampleStatus)
    colour = EnumField(Colour)
    biohazard_level = EnumField(BiohazardLevel)
    site_id = masql.auto_field()
    # current_site_id = masql.auto_field()

    quantity = masql.auto_field()
    disposal_id = masql.auto_field()
    consent_id = masql.auto_field()
    sample_to_type_id = masql.auto_field()


new_sample_schema = NewSampleSchema()

class EditSampleSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Sample

    barcode = masql.auto_field()
    source = EnumField(SampleSource)
    base_type = EnumField(SampleBaseType)
    status = EnumField(SampleStatus)
    colour = EnumField(Colour)
    biohazard_level = EnumField(BiohazardLevel)
    site_id = masql.auto_field()
    #current_site_id = masql.auto_field()

    quantity = masql.auto_field()
    remaining_quantity = masql.auto_field()
    disposal_id = masql.auto_field()
    consent_id = masql.auto_field()
    sample_to_type_id = masql.auto_field()


edit_sample_schema = EditSampleSchema()

class BasicSampleSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Sample

    id = masql.auto_field()
    is_locked = masql.auto_field()
    uuid = masql.auto_field()
    consent_information = ma.Nested(BasicConsentSchema, many=False)
    base_type = EnumField(SampleBaseType, by_value=True)
    quantity = masql.auto_field()
    remaining_quantity = masql.auto_field()
    status = EnumField(SampleStatus, by_value=True)

    colour = EnumField(Colour, by_value=True)
    source = EnumField(SampleSource, by_value=True)
    created_on = ma.Date()
    parent = ma.Nested(SampleUUIDSchema, many=False)

    sample_type_information = ma.Nested(SampleTypeSchema)
    storage = ma.Nested(EntityToStorageSchema, many=False)

    barcode = masql.auto_field()
    disposal_event = ma.Nested(BasicSampleDiposalEventSchema, many=False)
    _links = ma.Hyperlinks(
        {
            "add_sample_to_cart": ma.URLFor(
                "sample.add_sample_to_cart", uuid="<uuid>", _external=True
            ),
            "remove_sample_from_cart": ma.URLFor(
                "sample.remove_sample_from_cart", uuid="<uuid>", _external=True
            ),
            "remove_rack_from_cart": ma.URLFor(
                "sample.remove_rack_from_cart", id="<storage.rack_id>", _external=True
            ),
            "self": ma.URLFor("sample.view", uuid="<uuid>", _external=True),
            "collection": ma.URLFor("sample.index", _external=True),
            "barcode_generation": ma.URLFor(
                "api.misc_generate_barcode", _external=True
            ),
        }
    )


basic_sample_schema = BasicSampleSchema()
basic_samples_schema = BasicSampleSchema(many=True)


class SampleSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Sample

    id = masql.auto_field()

    uuid = masql.auto_field()
    base_type = EnumField(SampleBaseType, by_value=True)
    is_locked = masql.auto_field()
    is_closed = masql.auto_field()

    quantity = masql.auto_field()
    remaining_quantity = masql.auto_field()
    comments = masql.auto_field()
    barcode = masql.auto_field()
    sample_type_information = ma.Nested(SampleTypeSchema)

    colour = EnumField(Colour, by_value=True)
    source = EnumField(SampleSource, by_value=True)
    biohazard_level = EnumField(BiohazardLevel, by_value=True)
    status = EnumField(SampleSource, by_value=True)
    site_id = masql.auto_field()
    current_site_id = masql.auto_field()
    # author = ma.Nested(BasicUserAccountSchema, many=False)
    author = ma.Nested(UserAccountSearchSchema, many=False)

    disposal_information = ma.Nested(BasicSampleDisposalSchema, many=False)
    consent_information = ma.Nested(ConsentSchema, many=False)

    storage = ma.Nested(EntityToStorageSchema, many=False)

    attributes = ma.Nested(AttributeDataSchema, many=True)
    documents = ma.Nested(BasicDocumentSchema, many=True)

    parent = ma.Nested(BasicSampleSchema, many=False)
    subsamples = ma.Nested(BasicSampleSchema, many=True)

    events = ma.Nested(SampleProtocolEventSchema, many=True)
    subsample_event = ma.Nested(SampleProtocolEventSchema, many=False)
    reviews = ma.Nested(SampleReviewSchema, many=True)
    shipments = ma.Nested(SampleShipmentToSampleInfoSchema, many=True)

    created_on = ma.Date()

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("sample.view", uuid="<uuid>", _external=True),
            "add_sample_to_cart": ma.URLFor(
                "sample.add_sample_to_cart", uuid="<uuid>", _external=True
            ),
            "remove_sample_from_cart": ma.URLFor(
                "sample.remove_sample_from_cart", uuid="<uuid>", _external=True
            ),
            "collection": ma.URLFor("sample.index", _external=True),
            "webapp_query": ma.URLFor("sample.query", _external=True),
            "webapp_aliquot": ma.URLFor(
                "sample.aliquot_endpoint", uuid="<uuid>", _external=True
            ),
            "webapp_derive": ma.URLFor(
                "sample.derive_endpoint", uuid="<uuid>", _external=True
            ),
            "label": ma.URLFor("labels.sample_label", uuid="<uuid>", _external=True),
            "barcode_generation": ma.URLFor(
                "api.misc_generate_barcode",
                _external=True,
            ),
        }
    )


sample_schema = SampleSchema()
samples_schema = SampleSchema(many=True)


#
# class SubSampleToSampleSchema(masql.SQLAlchemySchema):
#     class Meta:
#         model = SubSampleToSample
#     parent_id = masql.auto_field()
#     subsample_id = masql.auto_field()
#
# class SampleProtocolEventViewSchema(masql.SQLAlchemySchema):
#     class Meta:
#         model = SampleProtocolEvent
#
#     is_locked = masql.auto_field()
#     uuid = masql.auto_field()
#     id = masql.auto_field()
#     reduced_quantity = masql.auto_field()
#     #author = ma.Nested(BasicUserAccountSchema)
#     author = ma.Nested(UserAccountSearchSchema)
#     event = ma.Nested(EventSchema)
#     created_on = ma.Date()
#
#     protocol = ma.Nested(BasicProtocolTemplateSchema)
#     subsamples_created = ma.Nested(SubSampleToSampleSchema)
#
#     _links = ma.Hyperlinks(
#         {
#             "edit": ma.URLFor(
#                 "sample.edit_protocol_event", uuid="<uuid>", _external=True
#             ),
#             "remove": ma.URLFor(
#                 "sample.remove_protocol_event", uuid="<uuid>", _external=True
#             ),
#         }
#     )
#
# sample_protocol_event_view_schema = SampleProtocolEventViewSchema()
# sample_protocol_events_view_schema = SampleProtocolEventViewSchema(many=True)
#
#
# class SampleViewSchema(masql.SQLAlchemySchema):
#     class Meta:
#         model = Sample
#
#     id = masql.auto_field()
#
#     uuid = masql.auto_field()
#     base_type = EnumField(SampleBaseType, by_value=True)
#     is_locked = masql.auto_field()
#     is_closed = masql.auto_field()
#
#     quantity = masql.auto_field()
#     remaining_quantity = masql.auto_field()
#     comments = masql.auto_field()
#     barcode = masql.auto_field()
#     sample_type_information = ma.Nested(SampleTypeSchema)
#
#     colour = EnumField(Colour, by_value=True)
#     source = EnumField(SampleSource, by_value=True)
#     biohazard_level = EnumField(BiohazardLevel, by_value=True)
#     status = EnumField(SampleSource, by_value=True)
#     site_id = masql.auto_field()
#     current_site_id = masql.auto_field()
#     # author = ma.Nested(BasicUserAccountSchema, many=False)
#     author = ma.Nested(UserAccountSearchSchema, many=False)
#
#     disposal_information = ma.Nested(BasicSampleDisposalSchema, many=False)
#     consent_information = ma.Nested(ConsentSchema, many=False)
#
#     storage = ma.Nested(EntityToStorageSchema, many=False)
#
#     attributes = ma.Nested(AttributeDataSchema, many=True)
#     documents = ma.Nested(BasicDocumentSchema, many=True)
#
#     parent = ma.Nested(BasicSampleSchema, many=False)
#     subsamples = ma.Nested(BasicSampleSchema, many=True)
#
#     events = ma.Nested(SampleProtocolEventViewSchema, many=True)
#     reviews = ma.Nested(SampleReviewSchema, many=True)
#     shipments = ma.Nested(SampleShipmentToSampleInfoSchema, many=True)
#
#     created_on = ma.Date()
#
#     _links = ma.Hyperlinks(
#         {
#             "self": ma.URLFor("sample.view", uuid="<uuid>", _external=True),
#             "add_sample_to_cart": ma.URLFor(
#                 "sample.add_sample_to_cart", uuid="<uuid>", _external=True
#             ),
#             "remove_sample_from_cart": ma.URLFor(
#                 "sample.remove_sample_from_cart", uuid="<uuid>", _external=True
#             ),
#             "collection": ma.URLFor("sample.index", _external=True),
#             "webapp_query": ma.URLFor("sample.query", _external=True),
#             "webapp_aliquot": ma.URLFor(
#                 "sample.aliquot_endpoint", uuid="<uuid>", _external=True
#             ),
#             "webapp_derive": ma.URLFor(
#                 "sample.derive_endpoint", uuid="<uuid>", _external=True
#             ),
#             "label": ma.URLFor("labels.sample_label", uuid="<uuid>", _external=True),
#             "barcode_generation": ma.URLFor(
#                 "api.misc_generate_barcode",
#                 _external=True,
#             ),
#         }
#     )
#
#
# sample_view_schema = SampleViewSchema()



