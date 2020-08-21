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

from ..extensions import ma
from ..database import Document, DocumentFile

import marshmallow_sqlalchemy as masql
from marshmallow import fields
from marshmallow_enum import EnumField
from .enums import DocumentType

from ..auth.views import BasicUserAccountSchema, UserAccountSearchSchema


class NewDocumentSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Document

    name = masql.auto_field()
    description = masql.auto_field()
    type = EnumField(DocumentType)


new_document_schema = NewDocumentSchema()


class BasicDocumentSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Document

    id = masql.auto_field()
    author = ma.Nested(BasicUserAccountSchema)
    name = masql.auto_field()
    type = EnumField(DocumentType)
    is_locked = masql.auto_field()
    created_on = fields.Date()

    _links = ma.Hyperlinks(
        {"self": ma.URLFor("document.view", id="id", _external=True), "collection": ma.URLFor("document.index", _external=True)}
    )


basic_document_schema = BasicDocumentSchema()
basic_documents_schema = BasicDocumentSchema(many=True)


class DocumentFileSchema(masql.SQLAlchemySchema):
    class Meta:
        model = DocumentFile

    id = masql.auto_field()
    name = masql.auto_field()
    checksum = masql.auto_field()
    document_id = masql.auto_field()
    path = masql.auto_field()
    created_on = fields.Date()
    author = ma.Nested(BasicUserAccountSchema)

    _links = ma.Hyperlinks(
        {"self": ma.URLFor("document.view", id="<id>", _external=True), "collection": ma.URLFor("document.index", _external=True)}
    )


document_file_schema = DocumentFileSchema()
document_files_schema = DocumentFileSchema(many=True)


class DocumentSearchSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Document

    id = masql.auto_field()
    name = masql.auto_field(required=False)
    description = masql.auto_field()
    type = EnumField(DocumentType)
    is_locked = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema)


class DocumentSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Document

    id = masql.auto_field(dump_only=True)
    name = masql.auto_field()
    description = masql.auto_field()
    type = EnumField(DocumentType)
    is_locked = masql.auto_field()
    created_on = fields.Date()
    author = ma.Nested(BasicUserAccountSchema)
    files = ma.Nested(DocumentFileSchema(many=True))


document_schema = DocumentSchema()
documents_schema = DocumentSchema(many=True)


class NewDocumentFileSchema(masql.SQLAlchemySchema):
    class Meta:
        model = DocumentFile

    name = masql.auto_field()
    checksum = masql.auto_field()
    document_id = masql.auto_field()
    path = masql.auto_field()


new_document_file_schema = NewDocumentFileSchema()
