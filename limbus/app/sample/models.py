from app import db
from .enums import SampleType, DisposalInstruction, SampleAttributeTypes, SampleStatus


class Sample(db.Model):
    __tablename__ = "samples"

    id = db.Column(db.Integer, primary_key=True)

    sample_type = db.Column(db.Enum(SampleType))
    collection_date = db.Column(db.DateTime)
    disposal_instruction = db.Column(db.Enum(DisposalInstruction))

    sample_status = db.Column(db.Enum(SampleStatus))

    disposal_date = db.Column(db.DateTime, nullable=False)

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))


class SampleProcessingTemplateAssociation(db.Model):
    __tablename__ = "sample_processing_tempalte_associations"

    id = db.Column(db.Integer, primary_key=True)

    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))
    template_id = db.Column(db.Integer, db.ForeignKey("processing_templates.id"))

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )


class SampleAttribute(db.Model):
    __tablename__ = "sample_attributes"

    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(128))
    accession = db.Column(db.String(64))
    ref = db.Column(db.String(64))
    type = db.Column(db.Enum(SampleAttributeTypes))

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )
    required = db.Column(db.Boolean(), default=False)


class SampleAttributeTextSetting(db.Model):
    __tablename__ = "sample_attribute_text_settings"

    id = db.Column(db.Integer, primary_key=True)
    max_length = db.Column(db.Integer, nullable=False)

    sample_attribute_id = db.Column(db.Integer, db.ForeignKey("sample_attributes.id"))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )


class SampleAttributeNumericSetting(db.Model):
    __tablename__ = "sample_attribute_numeric_settings"

    id = db.Column(db.Integer, primary_key=True)

    sample_attribute_id = db.Column(db.Integer, db.ForeignKey("sample_attributes.id"))
    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )


class SampleAttributeOption(db.Model):
    __tablename__ = "sample_attribute_options"

    id = db.Column(db.Integer, primary_key=True)

    term = db.Column(db.String(128))
    accession = db.Column(db.String(64))
    ref = db.Column(db.String(64))

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )
    sample_attribute_id = db.Column(db.Integer, db.ForeignKey("sample_attributes.id"))


class SampleAttributeTextValue(db.Model):
    __tablename__ = "sample_attribute_text_values"

    id = db.Column(db.Integer, primary_key=True)

    value = db.Column(db.String())

    sample_attribute_id = db.Column(db.Integer, db.ForeignKey("sample_attributes.id"))
    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)


class SampleAttributeOptionValue(db.Model):
    __tablename__ = "sample_attribute_option_value"
    id = db.Column(db.Integer, primary_key=True)

    sample_option_id = db.Column(
        db.Integer, db.ForeignKey("sample_attribute_options.id")
    )
    sample_attribute_id = db.Column(db.Integer, db.ForeignKey("sample_attributes.id"))
    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)


class SamplePatientConsentFormTemplateAssociation(db.Model):
    __tablename__ = "sample_pcf_associations"

    id = db.Column(db.Integer, primary_key=True)

    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))
    template_id = db.Column(db.Integer, db.ForeignKey("consent_form_templates.id"))

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)


class SamplePatientConsentFormAnswersAssociation(db.Model):
    __tablename__ = "pcf_answers"

    id = db.Column(db.Integer, primary_key=True)

    sample_pcf_association_id = db.Column(
        db.Integer, db.ForeignKey("sample_pcf_associations.id")
    )
    checked = db.Column(db.Integer, db.ForeignKey("consent_form_template_questions.id"))

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)


class SampleDocumentAssociation(db.Model):
    __tablename__ = "sample_document_associations"

    id = db.Column(db.Integer, primary_key=True)

    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id"))

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
