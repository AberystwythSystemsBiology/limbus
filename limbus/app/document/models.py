from app import db

class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String)

    description = db.Column(db.String)

    # type ENUM


    creation_date = db.Column(db.DateTime)
    upload_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now(), nullable=False)

    # Relationship to User
    uploader = db.Column(db.Integer, db.ForeignKey("users.id"))

    file_id = db.Column(db.Integer, db.ForeignKey("document_files.id"))

class DocumentFile(db.Model):
    __tablename__ = "document_files"
    id = db.Column(db.Integer, primary_key=True)
    file = db.Column(db.LargeBinary)



