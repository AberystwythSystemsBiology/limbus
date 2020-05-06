from app import db
from ..enums import *

class SampleProcessingTemplateAssociation(db.Model):
    __tablename__ = "sample_processing_tempalte_associations"

    id = db.Column(db.Integer, primary_key=True)

    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))
    template_id = db.Column(db.Integer, db.ForeignKey("processing_templates.id"))

    processing_date = db.Column(db.Date, nullable=False)
    processing_time = db.Column(db.Time, nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )
