from app import db
from .enums import SampleType, DisposalInstruction

class Sample(db.Model):
    __tablename__ = "samples"

    id = db.Column(db.Integer, primary_key=True)

    sample_type = db.Column(db.Enum(SampleType))
    datamatrix_barcode = db.Column(db.String)
    batch_number = db.Column(db.Integer)
    collection_date = db.Column(db.DateTime)
    disposal_instruction = db.Column(db.Enum(DisposalInstruction))

    donor_id = db.Column(db.Integer, db.ForeignKey("donors.id"))

class Donor(db.Model):
    __tablename__ = "donors"

    id = db.Column(db.Integer, primary_key=True)