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

import marshmallow_sqlalchemy as masql
from marshmallow import fields
from marshmallow_enum import EnumField
from .enums import ProtocolType, ProtocolTextType

from ..database import ProtocolTemplate, ProtocolText, ProtocolTemplateToDocument

import markdown

from ..auth.views import BasicUserAccountSchema, UserAccountSearchSchema
from ..document.views import BasicDocumentSchema


class MarkdownField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        return markdown.Markdown().convert(value)

    def _deserialize(self, value, attr, data, **kwargs):
        return "Goodbye World"


class ProtocolTemplateSearchSchema(masql.SQLAlchemySchema):
    class Meta:
        model = ProtocolTemplate

    id = masql.auto_field(required=False)
    name = masql.auto_field(required=False)
    type = fields.List(EnumField(ProtocolType, required=False))
    author = ma.Nested(UserAccountSearchSchema)
    is_locked = masql.auto_field(required=False)


class BasicProtocolTemplateSchema(masql.SQLAlchemySchema):
    class Meta:
        model = ProtocolTemplate

    id = masql.auto_field()
    name = masql.auto_field()
    type = EnumField(ProtocolType, by_value=True)
    author = ma.Nested(BasicUserAccountSchema)
    created_on = ma.Date()

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("protocol.view", id="<id>", _external=True),
            "collection": ma.URLFor("protocol.index", _external=True),
        }
    )


basic_protocol_template_schema = BasicProtocolTemplateSchema()
basic_protocol_templates_schema = BasicProtocolTemplateSchema(many=True)


class NewProtocolTemplateSchema(masql.SQLAlchemySchema):
    class Meta:
        model = ProtocolTemplate

    id = masql.auto_field()
    name = masql.auto_field()
    description = masql.auto_field()
    type = EnumField(ProtocolType)
    doi = masql.auto_field()


new_protocol_template_schema = NewProtocolTemplateSchema()
new_protocol_templates_schema = NewProtocolTemplateSchema(many=True)


class BasicProtocolTextSchema(masql.SQLAlchemySchema):
    class Meta:
        model = ProtocolText

    id = masql.auto_field()
    text = MarkdownField()
    type = EnumField(ProtocolTextType, by_value=True)
    author = ma.Nested(BasicUserAccountSchema)
    created_on = ma.Date()


basic_protocol_text_schema = BasicProtocolTextSchema()
basic_protocol_texts_schema = BasicProtocolTextSchema(many=True)


class NewProtocolTemplateToDocumentSchema(masql.SQLAlchemySchema):
    class Meta:
        model = ProtocolTemplateToDocument

    protocol_id = masql.auto_field()
    document_id = masql.auto_field()
    description = masql.auto_field()


new_protocol_template_to_document_schema = NewProtocolTemplateToDocumentSchema()


class ProtocolTemplateSchema(masql.SQLAlchemySchema):
    class Meta:
        model = ProtocolTemplate

    id = masql.auto_field()
    name = masql.auto_field()
    type = EnumField(ProtocolType, by_value=True)
    doi = masql.auto_field()
    description = masql.auto_field()
    author = ma.Nested(BasicUserAccountSchema)
    texts = ma.Nested(BasicProtocolTextSchema(many=True))
    documents = ma.Nested(BasicDocumentSchema(many=True))

    created_on = ma.Date()

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("protocol.view", id="id", _external=True),
            "collection": ma.URLFor("protocol.index", _external=True),
        }
    )


protocol_template_schema = ProtocolTemplateSchema()
protocol_templates_schema = ProtocolTemplateSchema(many=True)


class NewProtocolTextSchema(masql.SQLAlchemySchema):
    class Meta:
        model = ProtocolText

    text = masql.auto_field()
    type = EnumField(ProtocolTextType)


new_protocol_text_schema = NewProtocolTextSchema()
new_protocol_texts_schema = NewProtocolTextSchema(many=True)
