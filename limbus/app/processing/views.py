from .. import db
from .models import ProcessingTemplate
from ..auth.views import UserView

def ProcessingProtocolsIndexView() -> dict:
    protocols = db.session.query(ProcessingTemplate).all()

    data = {}

    for protocol in protocols:
        data[protocol.id] = {
            "name": protocol.name,
            "type": protocol.type,
            "sample_type": protocol.sample_type,
            "upload_type" : protocol.upload_type,
            "has_document": protocol.has_document,
            "upload_date" : protocol.upload_type,
            "user_information" : UserView(protocol.author_id)
        }

    return data


def ProcessingProtocolView(protocol_id) -> dict:
    pass