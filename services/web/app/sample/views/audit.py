from ...database import Sample, SampleProtocolEvent, SubSampleToSample
from ...event.views import EventSchema
from ...protocol.views import BasicProtocolTemplateSchema
from ...auth.views import BasicUserAccountSchema, UserAccountSearchSchema
from ...extensions import ma
from ..enums import SampleBaseType, Colour, SampleSource, SampleStatus, BiohazardLevel



from ...document.views import BasicDocumentSchema
from ...attribute.views import AttributeDataSchema
from ..views import SampleProtocolEventSchema, SampleReviewSchema#, SampleProtocolEventViewSchema

import marshmallow_sqlalchemy as masql
from marshmallow import fields
from marshmallow_enum import EnumField

from ...database import (
    Sample, SampleProtocolEvent, SubSampleToSample,
    SampleConsent,
)
from ...event.views import EventSchema
from ...protocol.views import BasicProtocolTemplateSchema
from ...auth.views import BasicUserAccountSchema, UserAccountSearchSchema
from ...extensions import ma
from ..enums import SampleBaseType, Colour, SampleSource, SampleStatus, BiohazardLevel


from . import *
# (
#     SampleUUIDSchema,
#     SampleTypeSchema,
#     BasicSampleSchema,
#     BasicSampleDisposalSchema,
#     BasicConsentSchema,
#     ConsentSchema,
#     EntityToStorageSchema,
#     BasicSampleDiposalEventSchema,
#     SampleShipmentToSampleInfoSchema,
#     BasicConsentFormTemplateSchema,
# )

from ...document.views import BasicDocumentSchema
from ...attribute.views import AttributeDataSchema
from ..views import SampleProtocolEventSchema, SampleReviewSchema#, SampleProtocolEventViewSchema

import marshmallow_sqlalchemy as masql
from marshmallow import fields
from marshmallow_enum import EnumField

from sqlalchemy_continuum import version_class
from sqlalchemy_continuum import transaction_class
from sqlalchemy_continuum import Operation

# SampleVersion = version_class(Sample)
#from ...FormEnum import FormEnum

# class OperationType(FormEnum):
#     0 = "INSERT"
#     1 = "UPDATE"
#     2 = "DELETE"


class AuditConsentSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(SampleConsent)

    id = masql.auto_field()
    identifier = masql.auto_field()
    donor_id = masql.auto_field()

    comments = masql.auto_field()
    undertaken_by = masql.auto_field()
    template = ma.Nested(BasicConsentFormTemplateSchema, many=False)
    template_questions = ma.Nested(BasicConsentFormQuestionSchema, many=True)
    date = ma.Date()
    answers = ma.Nested(BasicConsentFormQuestionSchema, many=True)
    withdrawn = masql.auto_field()
    withdrawal_date = ma.Date()
    study = ma.Nested(DonorProtocolEventSchema, many=False)

    # _links = ma.Hyperlinks(
    #     {
    #         "edit": ma.URLFor("donor.edit_donor_consent", id="<id>", donor_id="<donor_id>", _external=True),
    #         "remove": ma.URLFor("donor.remove_donor_consent", id="<id>", _external=True)
    #     })

    created_on = ma.Date()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    edited_on = ma.Date()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()  # masql.Enum(Operation, by_value=True)
    transaction_id = masql.auto_field()


audit_consent_schema = AuditConsentSchema()


class AuditSampleProtocolEventSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(SampleProtocolEvent)

    is_locked = masql.auto_field()
    uuid = masql.auto_field()
    id = masql.auto_field()
    reduced_quantity = masql.auto_field()
    #author = ma.Nested(BasicUserAccountSchema)
    #author = ma.Nested(UserAccountSearchSchema)
    event = ma.Nested(EventSchema)
    #created_on = ma.Date()

    protocol = ma.Nested(BasicProtocolTemplateSchema)

    created_on = ma.Date()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    edited_on = ma.Date()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field() #masql.Enum(Operation, by_value=True)
    transaction_id = masql.auto_field()

    # _links = ma.Hyperlinks(
    #     {
    #         "edit": ma.URLFor(
    #             "sample.edit_protocol_event", uuid="<uuid>", _external=True
    #         ),
    #         "remove": ma.URLFor(
    #             "sample.remove_protocol_event", uuid="<uuid>", _external=True
    #         ),
    #     }
    # )

audit_sample_protocol_event_schema = AuditSampleProtocolEventSchema()
audit_sample_protocol_events_schema = AuditSampleProtocolEventSchema(many=True)



class AuditSampleSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(Sample)


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

    consent_information = ma.Nested(AuditConsentSchema, many=False)
    disposal_information = ma.Nested(BasicSampleDisposalSchema, many=False)

    storage = ma.Nested(EntityToStorageSchema, many=False)

    attributes = ma.Nested(AttributeDataSchema, many=True)
    documents = ma.Nested(BasicDocumentSchema, many=True)

    #parent = ma.Nested(BasicSampleSchema, many=False)
    #subsamples = ma.Nested(BasicSampleSchema, many=True)

    events = ma.Nested(SampleProtocolEventSchema, many=True)
    reviews = ma.Nested(SampleReviewSchema, many=True)
    shipments = ma.Nested(SampleShipmentToSampleInfoSchema, many=True)

    created_on = ma.Date()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    edited_on = ma.Date()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field() #masql.Enum(Operation, by_value=True)
    transaction_id = masql.auto_field()


audit_sample_schema = AuditSampleSchema()
audit_samples_schema = AuditSampleSchema(many=True)




