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
from .enums import AttributeType, AttributeElementType

class Attribute(Base, RefAuthorMixin, RefEditorMixin):
    __tablename__ = "attribute"

    description = db.Column(db.Text)
    term = db.Column(db.String(128))
    accession = db.Column(db.String(64))
    ref = db.Column(db.String(64))
    required = db.Column(db.Boolean(), default=False)

    type = db.Column(db.Enum(AttributeType))
    element_type = db.Column(db.Enum(AttributeElementType))


class AttributeTextSetting(Base, RefAuthorMixin, RefEditorMixin):
    __tablename__ = "customattributetextsetting"
    max_length = db.Column(db.Integer, nullable=False)
    attribute_id = db.Column(db.Integer, db.ForeignKey("attribute.id"))


class AttributeNumericSetting(Base, RefAuthorMixin, RefEditorMixin):
    __tablename__ = "attributenumericsetting"

    attribute_id = db.Column(db.Integer, db.ForeignKey("attribute.id"))
    measurement = db.Column(db.String(32))
    prefix = db.Column(db.String(32))


class AttributeOption(Base, RefAuthorMixin, RefEditorMixin):
    __tablename__ = "attributeoption"

    term = db.Column(db.String(128))
    accession = db.Column(db.String(64))
    ref = db.Column(db.String(64))

    attribute_id = db.Column(db.Integer, db.ForeignKey("attribute.id"))