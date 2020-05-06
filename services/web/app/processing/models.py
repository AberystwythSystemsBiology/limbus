from app import db
from .enums import ProtocolSampleType, ProtocolUploadTypes, ProtocolTypes


class ProcessingTemplate(db.Model):
    __tablename__ = "processing_templates"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(128))
    type = db.Column(db.Enum(ProtocolTypes))

    sample_type = db.Column(db.Enum(ProtocolSampleType))

    upload_type = db.Column(db.Enum(ProtocolUploadTypes))

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    # has_template = db.Column(db.Boolean)
    has_document = db.Column(db.Boolean)

    upload_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )


class ProcessingTemplateToDocument(db.Model):
    __tablename__ = "processing_templates_to_documents"

    id = db.Column(db.Integer, primary_key=True)

    template_id = db.Column(db.Integer, db.ForeignKey("processing_templates.id"))
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id"))

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    upload_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )
