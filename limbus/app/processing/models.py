from app import db
from ..sample.enums import SampleType

from .enums import (
    FluidContainer,
    ProcessingTemps,
    ProcessingTimes,
    CentrifugationTime,
    CentrifugationWeights,
)


class ProcessingTemplate(db.Model):
    __tablename__ = "processing_templates"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(128))
    sample_type = db.Column(db.Enum(SampleType))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    has_template = db.Column(db.Boolean)
    has_document = db.Column(db.Boolean)

    upload_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )


class ProcessingTemplateFluidContainer(db.Model):
    __tablename__ = "processing_template_fluid_containers"
    id = db.Column(db.Integer, primary_key=True)

    container = db.Column(db.Enum(FluidContainer))
    template_id = db.Column(db.Integer, db.ForeignKey("processing_templates.id"))

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    upload_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )


class PreCentrifugeInformation(db.Model):
    __tablename__ = "pre_centrifuge_information"

    id = db.Column(db.Integer, primary_key=True)

    temp = db.Column(db.Enum(ProcessingTemps))
    time = db.Column(db.Enum(ProcessingTimes))

    template_id = db.Column(db.Integer, db.ForeignKey("processing_templates.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    upload_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )


class CentrifugeInformation(db.Model):
    __tablename__ = "centrifuge_information"

    id = db.Column(db.Integer, primary_key=True)

    temp = db.Column(db.Enum(ProcessingTemps))
    time = db.Column(db.Enum(CentrifugationTime))
    weight = db.Column(db.Enum(CentrifugationWeights))
    braking = db.Column(db.Boolean)

    second = db.Column(db.Boolean)

    template_id = db.Column(db.Integer, db.ForeignKey("processing_templates.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    upload_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )


class PostCentrifugeInformation(db.Model):
    __tablename__ = "post_centrifuge_information"

    id = db.Column(db.Integer, primary_key=True)

    temp = db.Column(db.Enum(ProcessingTemps))
    time = db.Column(db.Enum(ProcessingTimes))

    template_id = db.Column(db.Integer, db.ForeignKey("processing_templates.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    upload_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )
