from .. import db
from .models import ProcessingTemplate, ProcessingTemplateToDocument
from ..document.models import Document
from ..auth.views import UserView
from ..document.views import DocumentView


def ProcessingProtocolsIndexView() -> dict:
    protocols = db.session.query(ProcessingTemplate).all()

    data = {}

    for protocol in protocols:
        data[protocol.id] = {
            "name": protocol.name,
            "type": protocol.type,
            "sample_type": protocol.sample_type,
            "upload_type": protocol.upload_type,
            "has_document": protocol.has_document,
            "upload_date": protocol.upload_type,
            "user_information": UserView(protocol.author_id),
        }

    return data


def ProcessingProtocolView(protocol_id) -> dict:
    protocol = (
        db.session.query(ProcessingTemplate)
        .filter(ProcessingTemplate.id == protocol_id)
        .first_or_404()
    )

    data = {
        "id": protocol.id,
        "name": protocol.name,
        "type": protocol.type,
        "sample_type": protocol.sample_type,
        "upload_type": protocol.upload_type,
        "has_document": protocol.has_document,
        "upload_date": protocol.upload_type,
        "user_information": UserView(protocol.author_id),
        "documents": {},
    }

    for _, document in (
        db.session.query(ProcessingTemplateToDocument, Document)
        .filter(ProcessingTemplateToDocument.template_id == protocol_id)
        .filter(Document.id == ProcessingTemplateToDocument.document_id)
        .all()
    ):
        data["documents"][document.id] = DocumentView(document.id)

    return data
