# from services.web.app.database import Sample, SampleProtocolEvent, SubSampleToSample
# from services.web.app.event.views import EventSchema
# from services.web.app.protocol.views import BasicProtocolTemplateSchema
# from services.web.app.auth.views import BasicUserAccountSchema, UserAccountSearchSchema
# from services.web.app.extensions import ma
# from services.web.app.sample.enums import SampleBaseType, Colour, SampleSource, SampleStatus, BiohazardLevel
#
#
# from services.web.app.document.views import BasicDocumentSchema
# from services.web.app.attribute.views import AttributeDataSchema
# from services.web.app.sample.views import SampleProtocolEventSchema, SampleReviewSchema#, SampleProtocolEventViewSchema

import marshmallow_sqlalchemy as masql
from marshmallow import fields
from marshmallow_enum import EnumField

from ..database import (
    Sample,
    SampleProtocolEvent,
    SubSampleToSample,
    Event,
    SampleConsent,
    SampleConsentWithdrawal,
    SampleConsentAnswer,
    SampleShipment,
    SampleShipmentToSample,
    SampleShipmentStatus,
    SampleReview,
    SampleDisposal,
    Donor,
    DonorProtocolEvent,
    DonorDiagnosisEvent,
    ConsentFormTemplate,
    ConsentFormTemplateQuestion,
    ProtocolTemplate,
    UserAccount,
    SiteInformation,
    Address,
    EntityToStorage,
    ColdStorage,
    ColdStorageService,
)

from ..protocol.views import BasicProtocolTemplateSchema
from ..auth.views import UserAccountSearchSchema
from ..misc.views import SiteNameSchema
from ..storage.views import BasicSampleRackSchema, BasicColdStorageShelfSchema
from ..storage.enums import *
from ..extensions import ma
from ..sample.enums import *
from ..donor.enums import *
from ..protocol.enums import *
from ..consent.enums import *
from .enums import *
from ..auth.enums import *

# from ..sample.views import *

from ..document.views import BasicDocumentSchema
from ..attribute.views import AttributeDataSchema
from ..sample.views import (
    SampleTypeSchema,
    SampleReviewSchema,
)  # , SampleProtocolEventSchema, SampleProtocolEventViewSchema

import marshmallow_sqlalchemy as masql
from marshmallow import Schema, fields
from marshmallow_enum import EnumField
from sqlalchemy_continuum import version_class

# from sqlalchemy_continuum import transaction_class
# from sqlalchemy_continuum import Operation


class AuditFilterSchema(Schema):

    start_date = fields.String()
    end_date = fields.String()
    uuid = fields.String()
    site_id = fields.Int()
    user_id = fields.Int()
    audit_type = fields.String()
    audit_objects = fields.String()

    sample_object = fields.String()
    donor_object = fields.String()
    template_object = fields.String()
    auth_object = fields.String()
    storage_object = fields.String()

    source_study = fields.Int()


class AuditBasicConsentFormTemplateSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(ConsentFormTemplate)

    id = masql.auto_field()
    name = masql.auto_field()
    version = masql.auto_field()

    created_on = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = masql.auto_field()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("ConsentFormTemplate")


class AuditConsentFormTemplateQuestionSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(ConsentFormTemplateQuestion)

    id = masql.auto_field()
    question = masql.auto_field()
    type = EnumField(QuestionType, by_value=True)
    template_id = masql.auto_field()

    created_on = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = masql.auto_field()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("ConsentFormTemplateQuestion")


class AuditInfoConsentFormTemplateQuestionSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(ConsentFormTemplateQuestion)

    id = masql.auto_field()
    question = masql.auto_field()
    type = EnumField(QuestionType, by_value=True)
    template_id = masql.auto_field()

    # created_on = masql.auto_field()
    # author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = masql.auto_field()
    # editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()
    transaction_id = masql.auto_field()
    # end_transaction_id = masql.auto_field()
    # object = fields.Constant("ConsentFormTemplateQuestion")


class AuditEventSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(Event)

    id = masql.auto_field()
    datetime = masql.auto_field()
    undertaken_by = masql.auto_field()
    comments = masql.auto_field()

    created_on = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = masql.auto_field()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()  # masql.Enum(Operation, by_value=True)
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("Event")


audit_event_schema = AuditEventSchema()
audit_events_schema = AuditEventSchema(many=True)


class AuditInfoEventSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(Event)

    id = masql.auto_field()
    datetime = masql.auto_field()
    undertaken_by = masql.auto_field()
    comments = masql.auto_field()

    # created_on = masql.auto_field()
    # author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = masql.auto_field()
    # editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    # object = fields.Constant("Event")


class AuditDonorSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(Donor)

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

    created_on = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = masql.auto_field()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()  # masql.Enum(Operation, by_value=True)
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("Donor")


audit_donor_schema = AuditDonorSchema()


class AuditBasicDonorSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(Donor)

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

    created_on = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = masql.auto_field()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()  # masql.Enum(Operation, by_value=True)
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("Donor")


class AuditDonorProtocolEventSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(DonorProtocolEvent)

    id = masql.auto_field()
    uuid = masql.auto_field()
    is_locked = masql.auto_field()
    donor_id = masql.auto_field()
    reference_id = masql.auto_field()
    event = ma.Nested(AuditInfoEventSchema)
    # protocol_id = masql.auto_field()
    protocol = ma.Nested(BasicProtocolTemplateSchema)

    created_on = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = masql.auto_field()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()  # masql.Enum(Operation, by_value=True)
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("DonorProtocolEvent")


audit_donor_protocol_event_schema = AuditDonorProtocolEventSchema()


class AuditBasicDonorProtocolEventSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(DonorProtocolEvent)

    id = masql.auto_field()
    uuid = masql.auto_field()
    is_locked = masql.auto_field()
    donor_id = masql.auto_field()
    reference_id = masql.auto_field()
    event = ma.Nested(AuditInfoEventSchema)
    protocol_id = masql.auto_field()
    # protocol = ma.Nested(BasicProtocolTemplateSchema)
    created_on = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = masql.auto_field()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()  # masql.Enum(Operation, by_value=True)
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("DonorProtocolEvent")


class AuditDonorDiagnosisEventSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(DonorDiagnosisEvent)

    id = masql.auto_field()
    diagnosis_date = ma.Date()
    comments = masql.auto_field()
    doid_ref = masql.auto_field()
    stage = EnumField(CancerStage, by_values=True)

    created_on = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = masql.auto_field()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()  # masql.Enum(Operation, by_value=True)
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("DonorDiagnosisEvent")


class AuditSampleConsentSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(SampleConsent)

    id = masql.auto_field()
    identifier = masql.auto_field()
    donor_id = masql.auto_field()

    comments = masql.auto_field()
    undertaken_by = masql.auto_field()
    template = ma.Nested(AuditBasicConsentFormTemplateSchema, many=False)
    # template_questions = ma.Nested(ConsentFormQuestionSchema, many=True)
    date = ma.Date()
    answers = ma.Nested(AuditInfoConsentFormTemplateQuestionSchema, many=True)
    withdrawn = masql.auto_field()
    withdrawal_date = ma.Date()
    study = ma.Nested(AuditBasicDonorProtocolEventSchema, many=False)

    created_on = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = masql.auto_field()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()  # masql.Enum(Operation, by_value=True)
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("SampleConsent")


class AuditBasicSampleConsentSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(SampleConsent)

    id = masql.auto_field()
    identifier = masql.auto_field()
    donor_id = masql.auto_field()

    comments = masql.auto_field()
    undertaken_by = masql.auto_field()
    template_id = masql.auto_field()
    # template = ma.Nested(AuditBasicConsentFormTemplateSchema, many=False)
    # template_questions = ma.Nested(BasicConsentFormQuestionSchema, many=True)
    date = ma.Date()
    # answers = ma.Nested(BasicConsentFormQuestionSchema, many=True)
    withdrawn = masql.auto_field()
    withdrawal_date = ma.Date()
    # study = ma.Nested(DonorProtocolEventSchema, many=False)
    study_event_id = masql.auto_field()

    created_on = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = masql.auto_field()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("SampleConsent")


class AuditSampleConsentAnswerSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(SampleConsentAnswer)

    id = masql.auto_field()
    consent_id = masql.auto_field()
    question_id = masql.auto_field()

    created_on = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = masql.auto_field()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("SampleConsentAnswer")


class AuditBasicSampleConsentWithdrawalSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(SampleConsentWithdrawal)

    id = masql.auto_field()
    consent_id = masql.auto_field()
    withdrawal_reason = masql.auto_field()
    requested_by = masql.auto_field()
    future_consent_id = masql.auto_field()
    event_id = masql.auto_field()

    created_on = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = masql.auto_field()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()  # masql.Enum(Operation, by_value=True)
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("SampleConsentWithdrawal")


class AuditSampleProtocolEventSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(SampleProtocolEvent)

    is_locked = masql.auto_field()
    uuid = masql.auto_field()
    id = masql.auto_field()
    reduced_quantity = masql.auto_field()
    # author = ma.Nested(UserAccountSearchSchema)
    event = ma.Nested(AuditInfoEventSchema)
    protocol = ma.Nested(BasicProtocolTemplateSchema)

    created_on = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = masql.auto_field()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()  # masql.Enum(Operation, by_value=True)
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("SampleProtocolEvent")


audit_sample_protocol_event_schema = AuditSampleProtocolEventSchema()
audit_sample_protocol_events_schema = AuditSampleProtocolEventSchema(many=True)


class AuditBasicSampleProtocolEventSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(SampleProtocolEvent)

    is_locked = masql.auto_field()
    uuid = masql.auto_field()
    id = masql.auto_field()
    reduced_quantity = masql.auto_field()
    event = ma.Nested(AuditInfoEventSchema)
    protocol_id = masql.auto_field()
    # protocol = ma.Nested(BasicProtocolTemplateSchema)

    created_on = masql.auto_field()
    author_id = masql.auto_field
    # author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = masql.auto_field()
    editor_id = masql.auto_field
    # editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("SampleProtocolEvent")


audit_basic_sample_protocol_event_schema = AuditBasicSampleProtocolEventSchema()
audit_basic_sample_protocol_events_schema = AuditBasicSampleProtocolEventSchema(
    many=True
)


class AuditSampleDisposalSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(SampleDisposal)

    id = masql.auto_field()
    sample_id = masql.auto_field()
    instruction = EnumField(DisposalInstruction, by_value=True)
    comments = masql.auto_field()
    disposal_date = masql.auto_field()
    review_event_id = masql.auto_field()
    approval_event_id = masql.auto_field()
    # disposal_event_id = masql.auto_field()
    # review_event = ma.Nested(SampleReviewSchema)
    disposal_event = ma.Nested(AuditBasicSampleProtocolEventSchema)
    created_on = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = masql.auto_field()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()  # masql.Enum(Operation, by_value=True)
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("SampleDisposal")


audit_sample_disposal_schema = AuditSampleDisposalSchema()


class AuditBasicSampleDisposalSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(SampleDisposal)

    id = masql.auto_field()
    sample_id = masql.auto_field()
    instruction = EnumField(DisposalInstruction, by_value=True)
    comments = masql.auto_field()
    disposal_date = masql.auto_field()
    review_event_id = masql.auto_field()
    approval_event_id = masql.auto_field()
    # disposal_event_id = masql.auto_field()
    review_event_id = masql.auto_field()
    # review_event = ma.Nested(SampleReviewSchema)
    disposal_event_id = masql.auto_field()
    # disposal_event = ma.Nested(SampleProtocolEventSchema)

    created_on = masql.auto_field()
    author_id = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = masql.auto_field()
    editor_id = masql.auto_field()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()  # masql.Enum(Operation, by_value=True)
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("SampleDisposal")


class AuditEntityToStorageSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(EntityToStorage)
        #model = EntityToStorage

    id = masql.auto_field()
    storage_type = EnumField(EntityToStorageType)

    rack = ma.Nested(BasicSampleRackSchema, many=False)
    shelf = ma.Nested(BasicColdStorageShelfSchema, many=False)
    sample_id = masql.auto_field()
    # rack_id = masql.auto_field()
    # shelf_id = masql.auto_field()
    row = masql.auto_field()
    col = masql.auto_field()
    entry_datetime = masql.auto_field()
    entry = masql.auto_field()
    removed = masql.auto_field()

    created_on = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = masql.auto_field()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field() #masql.Enum(Operation, by_value=True)
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("EntityToStorage")


class AuditBasicEntityToStorageSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(EntityToStorage)
        # model = EntityToStorage

    id = masql.auto_field()
    storage_type = EnumField(EntityToStorageType)
    rack_id = masql.auto_field()
    # rack = ma.Nested(BasicSampleRackSchema, many=False)
    shelf_id = masql.auto_field()
    # shelf = ma.Nested(BasicColdStorageShelfSchema, many=False)
    sample_id = masql.auto_field()
    row = masql.auto_field()
    col = masql.auto_field()
    entry_datetime = masql.auto_field()
    entry = masql.auto_field()
    removed = masql.auto_field()

    created_on = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = masql.auto_field()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("EntityToStorage")


audit_basic_entitytostorage_schema = AuditBasicEntityToStorageSchema()
audit_basic_entitytostorages_schema = AuditBasicEntityToStorageSchema(many=True)


class AuditBasicSampleShipmentSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(SampleShipment)

    uuid = masql.auto_field()
    id = masql.auto_field()
    new_site = ma.Nested(SiteNameSchema, many=False)
    created_on = ma.Date()
    # shipment_status = ma.Nested(BasicSampleShipmentStatusSchema)  # , many=False)
    event = ma.Nested(AuditInfoEventSchema)

    created_on = ma.Date()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = ma.Date()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()  # masql.Enum(Operation, by_value=True)
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("SampleShipment")


class AuditInfoSampleShipmentSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(SampleShipment)

    uuid = masql.auto_field()
    id = masql.auto_field()
    new_site = ma.Nested(SiteNameSchema, many=False)
    event_id = masql.auto_field()  # ma.Nested(AuditInfoEventSchema)

    updated_on = ma.Date()
    operation_type = masql.auto_field()  # masql.Enum(Operation, by_value=True)
    transaction_id = masql.auto_field()


class AuditSampleShipmentToSampleSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(SampleShipmentToSample)

    shipment = ma.Nested(AuditInfoSampleShipmentSchema, many=False)
    old_site = ma.Nested(SiteNameSchema, many=False)

    created_on = ma.Date()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = ma.Date()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()  # masql.Enum(Operation, by_value=True)
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("SampleShipmentToSample")


class AuditBasicSampleShipmentToSampleSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(SampleShipmentToSample)

    id = masql.auto_field()
    shipment_id = masql.auto_field()
    sample_id = masql.auto_field()
    # shipment = ma.Nested(BasicSampleShipmentSchema, many=False)
    old_site = ma.Nested(SiteNameSchema, many=False)

    created_on = ma.Date()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = ma.Date()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()  # masql.Enum(Operation, by_value=True)
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("SampleShipmentToSample")


class AuditBasicSampleShipmentStatusSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(SampleShipmentStatus)

    id = masql.auto_field()
    shipment_id = masql.auto_field()
    status = EnumField(SampleShipmentStatusStatus, by_value=True)
    datetime = masql.auto_field()
    comments = masql.auto_field()
    tracking_number = masql.auto_field()

    created_on = ma.Date()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = ma.Date()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()  # masql.Enum(Operation, by_value=True)
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("SampleShipmentStatus")


class AuditSampleReviewSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(SampleReview)

    id = masql.auto_field()
    uuid = masql.auto_field()
    quality = EnumField(SampleQuality, by_value=True)
    review_type = EnumField(ReviewType, by_value=True)
    result = EnumField(ReviewResult, by_value=True)
    event = ma.Nested(AuditInfoEventSchema)

    created_on = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = masql.auto_field()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("SampleReview")


audit_sample_review_schema = AuditSampleReviewSchema()
audit_sample_reviews_schema = AuditSampleReviewSchema(many=True)


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

    consent_information = ma.Nested(AuditSampleConsentSchema, many=False)
    disposal_information = ma.Nested(AuditSampleDisposalSchema, many=False)

    storage = ma.Nested(AuditEntityToStorageSchema, many=False)

    attributes = ma.Nested(AttributeDataSchema, many=True)
    documents = ma.Nested(BasicDocumentSchema, many=True)

    # parent = ma.Nested(BasicSampleSchema, many=False)
    # subsamples = ma.Nested(BasicSampleSchema, many=True)

    events = ma.Nested(AuditBasicSampleProtocolEventSchema, many=True)
    reviews = ma.Nested(AuditSampleReviewSchema, many=True)
    shipments = ma.Nested(AuditBasicSampleShipmentToSampleSchema, many=True)

    created_on = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = masql.auto_field()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()  # masql.Enum(Operation, by_value=True)
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("Sample")


audit_sample_schema = AuditSampleSchema()
audit_samples_schema = AuditSampleSchema(many=True)


class AuditBasicSampleSchema(masql.SQLAlchemySchema):
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
    sample_to_type_id = masql.auto_field()
    # sample_type_information = ma.Nested(SampleTypeSchema)

    colour = EnumField(Colour, by_value=True)
    source = EnumField(SampleSource, by_value=True)
    biohazard_level = EnumField(BiohazardLevel, by_value=True)
    status = EnumField(SampleSource, by_value=True)
    site_id = masql.auto_field()
    current_site_id = masql.auto_field()
    consent_id = masql.auto_field()
    disposal_id = masql.auto_field()

    created_on = masql.auto_field()
    author_id = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = masql.auto_field()
    editor_id = masql.auto_field()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()  # masql.Enum(Operation, by_value=True)
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("Sample")


audit_basic_sample_schema = AuditBasicSampleSchema()
audit_basic_samples_schema = AuditBasicSampleSchema(many=True)


class AuditBasicProtocolTemplateSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(ProtocolTemplate)

    id = masql.auto_field()
    name = masql.auto_field()
    doi = masql.auto_field()
    type = EnumField(ProtocolType, by_value=True)

    created_on = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = masql.auto_field()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("ProtocolTemplate")


class AuditBasicUserAccountSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(UserAccount)

    id = masql.auto_field()
    email = masql.auto_field()
    first_name = masql.auto_field()
    last_name = masql.auto_field()
    account_type = EnumField(AccountType, by_value=True)
    is_locked = masql.auto_field()
    site_id = masql.auto_field()
    settings = masql.auto_field()

    created_on = masql.auto_field()
    updated_on = masql.auto_field()
    operation_type = masql.auto_field()
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("UserAccount")


class AuditBasicAddressSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(Address)

    id = masql.auto_field()
    street_address_one = masql.auto_field()
    street_address_two = masql.auto_field()
    city = masql.auto_field()
    county = masql.auto_field()
    post_code = masql.auto_field()
    country = masql.auto_field()
    site_id = masql.auto_field()

    created_on = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = masql.auto_field()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("Address")


class AuditInfoAddressSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(Address)

    id = masql.auto_field()
    street_address_one = masql.auto_field()
    street_address_two = masql.auto_field()
    city = masql.auto_field()
    county = masql.auto_field()
    post_code = masql.auto_field()
    country = masql.auto_field()
    site_id = masql.auto_field()
    updated_on = masql.auto_field()
    operation_type = masql.auto_field()
    transaction_id = masql.auto_field()


class AuditSiteInformationSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(SiteInformation)

    id = masql.auto_field()

    miabis_id = masql.auto_field()
    acronym = masql.auto_field()
    address = ma.Nested(AuditInfoAddressSchema)
    name = masql.auto_field()
    description = masql.auto_field()
    url = masql.auto_field()

    is_locked = masql.auto_field()
    is_external = masql.auto_field()

    created_on = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = masql.auto_field()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("SiteInformation")


class AuditBasicColdStorageSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(ColdStorage)

    id = masql.auto_field()
    alias = masql.auto_field()
    is_locked = masql.auto_field()
    uuid = masql.auto_field()
    serial_number = masql.auto_field()
    manufacturer = masql.auto_field()
    temp = EnumField(FixedColdStorageTemps, by_value=True)
    type = EnumField(FixedColdStorageType, by_value=True)
    room_id = masql.auto_field()
    # shelves = ma.Nested(ColdStorageShelfSchema, many=True)
    status = EnumField(FixedColdStorageStatus, by_value=True)
    # service_history = ma.Nested(ColdStorageServiceSchema, many=True)
    # documents = ma.Nested(DocumentSchema(), many=True)

    created_on = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = masql.auto_field()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("ColdStorage")


class AuditColdStorageServiceSchema(masql.SQLAlchemySchema):
    class Meta:
        model = version_class(ColdStorageService)

    id = masql.auto_field()
    date = masql.auto_field()
    conducted_by = masql.auto_field()
    status = EnumField(ColdStorageServiceResult, by_value=True)
    comments = masql.auto_field()
    temp = masql.auto_field()

    created_on = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema, many=False)
    updated_on = masql.auto_field()
    editor = ma.Nested(UserAccountSearchSchema, many=False)
    operation_type = masql.auto_field()
    transaction_id = masql.auto_field()
    end_transaction_id = masql.auto_field()
    object = fields.Constant("ColdStorageService")
