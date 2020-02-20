from app import db
from enum import Enum


class DocumentType(Enum):
    PATHO = "Pathology Reports"
    PATIE = "Patient Consent Forms"
    MANUE = "Device Manuals"
    MATER = "Material Transfer Agreements"
    OTHER = "Other"


class Document(db.Model):
    __tablename__ = "documents"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    type = db.Column(db.Enum(DocumentType))
    other_type = db.Column(db.String(128))
    description = db.Column(db.String)
    upload_date = db.Column(db.DateTime,
                            server_default=db.func.now(),
                            nullable=False)
    update_date = db.Column(db.DateTime,
                            server_default=db.func.now(),
                            server_onupdate=db.func.now(),
                            nullable=False)
    # Relationship to User
    uploader = db.Column(db.Integer, db.ForeignKey("users.id"))


class DocumentFile(db.Model):
    __tablename__ = "document_files"
    id = db.Column(db.Integer, primary_key=True)

    filename = db.Column(db.String)
    filepath = db.Column(db.String)

    upload_date = db.Column(db.DateTime,
                            server_default=db.func.now(),
                            nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id"))

    uploader = db.Column(db.Integer, db.ForeignKey("users.id"))


class PatientConsentForm(db.Model):
    __tablename__ = "patient_consent_forms"

    id = db.Column(db.Integer, primary_key=True)

    academic = db.Column(db.Boolean)
    commercial = db.Column(db.Boolean)
    animal = db.Column(db.Boolean)
    genetic = db.Column(db.Boolean)

    indefinite = db.Column(db.Boolean)

    upload_date = db.Column(db.DateTime,
                            server_default=db.func.now(),
                            nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id"))

    uploader = db.Column(db.Integer, db.ForeignKey("users.id"))


class PatientConsentWithdrawalDate(db.Model):
    __tablename__ = "patitent_consent_withdrawal_date"

    id = db.Column(db.Integer, primary_key=True)

    withdrawal_date = db.Column(db.DateTime, nullable=False)

    upload_date = db.Column(db.DateTime,
                            server_default=db.func.now(),
                            nullable=False)
    patient_consent_id = db.Column(db.Integer,
                                   db.ForeignKey("patient_consent_forms.id"))
