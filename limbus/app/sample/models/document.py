from app import db

class SampleDocumentAssociation(db.Model):
    __tablename__ = "sample_document_associations"

    id = db.Column(db.Integer, primary_key=True)

    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id"))

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
