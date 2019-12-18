from app import db
from .enums import SampleType, DisposalInstruction, SampleAttributeTypes

class Sample(db.Model):
    __tablename__ = "samples"

    id = db.Column(db.Integer, primary_key=True)

    sample_type = db.Column(db.Enum(SampleType))
    collection_date = db.Column(db.DateTime)
    disposal_instruction = db.Column(db.Enum(DisposalInstruction))
    #disposal_date = db.Column(db.DateTime, nullable=False)

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now(), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    donor_id = db.Column(db.Integer, db.ForeignKey("donors.id"))

class SampleAttribute(db.Model):
    __tablename__ = "sample_attributes"

    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(128))
    accession = db.Column(db.String(64))
    ref = db.Column(db.String(64))
    type = db.Column(db.Enum(SampleAttributeTypes))

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now(), nullable=False)
    required = db.Column(db.Boolean(), default=False)


class SampleAttributeOption(db.Model):
    __tablename__ = "sample_attribute_options"

    id = db.Column(db.Integer, primary_key=True)

    term = db.Column(db.String(128))
    accession = db.Column(db.String(64))
    ref = db.Column(db.String(64))

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now(), nullable=False)
    sample_attribute_id = db.Column(db.Integer, db.ForeignKey("sample_attributes.id"))

class Donor(db.Model):
    __tablename__ = "donors"

    id = db.Column(db.Integer, primary_key=True)
    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now(), nullable=False)