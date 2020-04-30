from .. import db
from .models import Document, DocumentFile
from ..auth.views import UserView

def DocumentIndexView():
    documents = db.session.query(Document).all()

    data = {}

    for document in documents:
        data[document.id] = {
            "name": document.name,
            "type": document.type,
            "description": document.description,
            "upload_date": document.upload_date,
            "user_information" : UserView(document.uploader)
        }

    return data

def DocumentView(doc_id: int) -> dict:
    document = db.session.query(Document).filter(Document.id == doc_id).first_or_404()

    files = {}

    for file in db.session.query(DocumentFile).filter(DocumentFile.document_id == doc_id).all():
        files[file.id] = {
            "filename": file.filename,
            "filepath": file.filepath,
            "upload_date": file.upload_date,
            "user_information" : UserView(file.uploader)
        }

    return {
        "id": document.id,
        "name": document.name,
        "description": document.description,
        "upload_date": document.upload_date,
        "update_data" : document.update_date,
        "user_information": UserView(document.uploader),
        "files" : files
    }