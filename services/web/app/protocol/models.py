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


from app import db, Base

from ..mixins import RefAuthorMixin, RefEditorMixin
from .enums import ProtocolType, ProtocolTextType


class ProtocolTemplate(Base, RefAuthorMixin, RefEditorMixin):
    __tablename__ = "protocoltemplate"

    name = db.Column(db.String(128), nullable=False)
    type = db.Column(db.Enum(ProtocolType))
    doi = db.Column(db.String(64))
    texts = db.relationship("ProtocolText", uselist=True)
    documents = db.relationship("Document", uselist=True, secondary='protocoltemplatetodocument')

class ProtocolTemplateToDocument(Base, RefAuthorMixin, RefEditorMixin):
    __tablename__ = "protocoltemplatetodocument"

    protocol_id = db.Column(db.Integer, db.ForeignKey("protocoltemplate.id"), nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey("document.id"), nullable=False)

class ProtocolText(Base, RefAuthorMixin, RefEditorMixin):
    __tablename__ = "processingtemplatematerialsandreagents"

    text = db.Column(db.Text(), nullable=False)
    type = db.Column(db.Enum(ProtocolTextType))
    protocol_id = db.Column(db.Integer, db.ForeignKey("protocoltemplate.id"), nullable=False)