from app import db
from enum import Enum

class SampleType(Enum):
    FLU = "Fluid"
    TIS = "Tissue"

class FluidSampleType(Enum):
    ASC = "Ascites fluid"
    AMN = "Amniotic fluid"
    BAL = "Bronchoalveolar lavage"
    BLD = "Blood (whole)"
    BMA = "Bone marrow aspirate"
    BMK = "Breast milk"
    BUC = "Buccal cells"
    BUF = "Unficolled buffy coat, viable"
    BFF = "Unficolled buffy coat, non-viable"
    CEL = "Ficoll mononuclear cells, viable"
    CEN = "Fresh cells from non-blood specimen type"

class DisposalInstruction(Enum):
    DES = "Destroy"
    TRA = "Transfer"
    REV = "Note for Review"
    PRE = "Preserve"

class SampleStatus(Enum):
    AVA = "Available"
    DES = "Destroyed"
    TRA = "Transferred"
    MIS = "Missing"

class Sample(db.Model):
    __tablename__ = "samples"

    id = db.Column(db.Integer, primary_key=True)

    sample_type = db.Column(db.Enum(SampleType))
    datamatrix_barcode = db.Column(db.String)
    batch_number = db.Column(db.Integer)
    collection_date = db.Column(db.DateTime)

    donor_id = db.Column(db.Integer, db.ForeignKey("donors.id"))

class Donor(db.Model):
    __tablename__ = "donors"

    id = db.Column(db.Integer, primary_key=True)