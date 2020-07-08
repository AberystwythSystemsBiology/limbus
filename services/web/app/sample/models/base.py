from app import db
from ..enums import *


class Sample(db.Model):
    __tablename__ = "samples"

    id = db.Column(db.Integer, primary_key=True)
    # UUID4 length = 36
    uuid = db.Column(db.String(36))
    biobank_barcode = db.Column(db.String)

    sample_type = db.Column(db.Enum(SampleType))
    collection_date = db.Column(db.DateTime)
    sample_status = db.Column(db.Enum(SampleStatus))

    quantity = db.Column(db.Float)
    current_quantity = db.Column(db.Float)

    is_closed = db.Column(db.Boolean)

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))


class SampleDisposalInformation(db.Model):
    __tablename__ = "sample_disposal_instruction"
    id = db.Column(db.Integer, primary_key=True)

    disposal_instruction = db.Column(db.Enum(DisposalInstruction))
    disposal_date = db.Column(db.DateTime, nullable=True)

    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))


class SampleToDonor(db.Model):
    __tablename__ = "sample_to_donors"
    id = db.Column(db.Integer, primary_key=True)

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))
    donor_id = db.Column(db.Integer, db.ForeignKey("donors.id"))

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
