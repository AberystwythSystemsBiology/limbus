# Copyright (C) 2019  Keiron O'Shea <keo7@aber.ac.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
