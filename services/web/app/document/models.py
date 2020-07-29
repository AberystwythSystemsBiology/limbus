from app import db, Base
from enum import Enum
from ..mixins import RefAuthorMixin


class DocumentType(Enum):
    PATHO = "Pathology Report"
    MANUE = "Device Manual"
    MATER = "Material Transfer Agreement"
    PROTO = "Processing Protocol"
    OTHER = "Other"


class Document(Base, RefAuthorMixin):
    __tablename__ = "document"
    __versioned__ = {}
    name = db.Column(db.String, nullable=False)
    type = db.Column(db.Enum(DocumentType))
    other_type = db.Column(db.String(128))
    description = db.Column(db.String)
    files = db.relationship("DocumentFile")

class DocumentFile(Base, RefAuthorMixin):
    __tablename__ = "documentfile"

    filename = db.Column(db.String, nullable=False)
    filepath = db.Column(db.String)
    document_id = db.Column(db.Integer, db.ForeignKey("document.id"))