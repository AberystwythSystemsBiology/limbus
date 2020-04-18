from app import db
from ..enums import *

class Sample(db.Model):
    __tablename__ = "samples"

    id = db.Column(db.Integer, primary_key=True)

    sample_type = db.Column(db.Enum(SampleType))
    collection_date = db.Column(db.DateTime)
    disposal_instruction = db.Column(db.Enum(DisposalInstruction))
    sample_status = db.Column(db.Enum(SampleStatus))

    quantity = db.Column(db.Float)
    current_quantity = db.Column(db.Float)

    disposal_date = db.Column(db.DateTime, nullable=False)

    is_closed = db.Column(db.Boolean)

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
