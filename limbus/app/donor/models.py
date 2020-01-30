from app import db
from .enums import DonorSex, DonorRace, DonorDiagnosticProcedureType

class Donor(db.Model):
    __tablename__ = "donors"

    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer)

    race = db.Column(db.Enum(DonorRace))

    height = db.Column(db.Integer)
    weight = db.Column(db.Integer)

    sex = db.Column(db.Enum(DonorSex))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now(), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

class DonorDiagnosis(db.Model):
    __tablename__ = "donor_diagnoses"

    id = db.Column(db.Integer, primary_key=True)
    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now(), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

class DonorVisitNumber(db.Model):
    __tablename__ = "donor_visit_numbers"

    id = db.Column(db.Integer, primary_key=True)

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now(), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

class DonorDiagnosticProcedureInformation(db.Model):
    __tablename__ = "donor_diag_proc_info"
    id = db.Column(db.Integer, primary_key=True)

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now(), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))