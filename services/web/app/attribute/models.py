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

from ..database import db, Base
from ..mixins import RefAuthorMixin, RefEditorMixin
from .enums import AttributeType, AttributeElementType, AttributeTextSettingType


class Attribute(Base, RefAuthorMixin, RefEditorMixin):
    description = db.Column(db.Text)
    term = db.Column(db.String(128))
    accession = db.Column(db.String(64))
    ref = db.Column(db.String(64))
    required = db.Column(db.Boolean(), default=False)

    text_setting = db.relationship(
        "AttributeTextSetting", uselist=False, cascade="all, delete"
    )
    numeric_setting = db.relationship(
        "AttributeNumericSetting", uselist=False, cascade="all, delete"
    )
    options = db.relationship("AttributeOption", cascade="all, delete")

    type = db.Column(db.Enum(AttributeType))
    element_type = db.Column(db.Enum(AttributeElementType))


class AttributeTextSetting(Base, RefAuthorMixin, RefEditorMixin):
    max_length = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Enum(AttributeTextSettingType))
    attribute_id = db.Column(
        db.Integer, db.ForeignKey("attribute.id", use_alter=True), unique=True
    )


class AttributeNumericSetting(Base, RefAuthorMixin, RefEditorMixin):
    attribute_id = db.Column(
        db.Integer, db.ForeignKey("attribute.id", use_alter=True), unique=True
    )
    measurement = db.Column(db.String(32))
    symbol = db.Column(db.String(32))


class AttributeOption(Base, RefAuthorMixin, RefEditorMixin):
    term = db.Column(db.String(128))
    accession = db.Column(db.String(64))
    ref = db.Column(db.String(64))
    attribute_id = db.Column(db.Integer, db.ForeignKey("attribute.id", use_alter=True))


class AttributeData(Base, RefAuthorMixin, RefEditorMixin):
    attribute_id = db.Column(
        db.Integer, db.ForeignKey("attribute.id", use_alter=True), nullable=False
    )
    attribute = db.relationship("Attribute", uselist=False)
    option_id = db.Column(
        db.Integer, db.ForeignKey("attributeoption.id", use_alter=True)
    )
    option = db.relationship("AttributeOption", uselist=False)
    data = db.Column(db.Text)
