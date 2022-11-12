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

from ..database import (
    Attribute,
    AttributeTextSetting,
    AttributeNumericSetting,
    AttributeOption,
    AttributeData,
)

import marshmallow_sqlalchemy as masql
from marshmallow import fields
from marshmallow_enum import EnumField

from ..auth.views import BasicUserAccountSchema, UserAccountSearchSchema

from .enums import AttributeType, AttributeElementType, AttributeTextSettingType


class AttributeSearchSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Attribute

    is_locked = masql.auto_field()
    element_type = fields.List(EnumField(AttributeElementType, required=False))
    type = EnumField(AttributeType, required=False)


class BasicAttributeSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Attribute

    id = masql.auto_field()
    is_locked = masql.auto_field()
    term = masql.auto_field()
    description = masql.auto_field()
    author = ma.Nested(BasicUserAccountSchema)
    created_on = fields.Date()
    type = EnumField(AttributeType, by_value=True)
    element_type = EnumField(AttributeElementType, by_value=True)


basic_attribute_schema = BasicAttributeSchema()
basic_attributes_schema = BasicAttributeSchema(many=True)


class NewAttributeSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Attribute

    term = masql.auto_field()
    description = masql.auto_field()
    accession = masql.auto_field()
    ref = masql.auto_field()
    type = EnumField(AttributeType)
    element_type = EnumField(AttributeElementType)


new_attribute_schema = NewAttributeSchema()


class EditAttributeSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Attribute

    term = masql.auto_field()
    description = masql.auto_field()
    accession = masql.auto_field()
    ref = masql.auto_field()
    element_type = EnumField(AttributeElementType)


edit_attribute_schema = EditAttributeSchema()


class NewAttributeTextSettingSchema(masql.SQLAlchemySchema):
    class Meta:
        model = AttributeTextSetting

    max_length = masql.auto_field()
    type = EnumField(AttributeTextSettingType)


new_attribute_text_setting_schema = NewAttributeTextSettingSchema()


class NewAttributeNumericSettingSchema(masql.SQLAlchemySchema):
    class Meta:
        model = AttributeNumericSetting

    symbol = masql.auto_field()
    measurement = masql.auto_field()


new_attribute_numeric_setting_schema = NewAttributeNumericSettingSchema()


class NewAttributeOptionSchema(masql.SQLAlchemySchema):
    class Meta:
        model = AttributeOption

    attribute_id = masql.auto_field(allow_none=False)
    term = masql.auto_field(allow_none=False)
    accession = masql.auto_field(allow_none=True)
    ref = masql.auto_field(allow_none=True)


new_attribute_option_schema = NewAttributeOptionSchema()
new_attribute_options_schema = NewAttributeOptionSchema(many=True)


class AttributeOptionSchema(masql.SQLAlchemySchema):
    class Meta:
        model = AttributeOption

    id = masql.auto_field()
    term = masql.auto_field()
    accession = masql.auto_field()
    ref = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema)
    is_locked = ma.auto_field()
    created_on = fields.Date()


attribute_option_schema = AttributeOptionSchema()
attribute_options_schema = AttributeOptionSchema(many=True)


class AttributeSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Attribute

    id = masql.auto_field()
    is_locked = masql.auto_field()
    term = masql.auto_field()
    description = masql.auto_field()
    accession = masql.auto_field()
    ref = masql.auto_field

    author = ma.Nested(UserAccountSearchSchema)
    created_on = fields.Date()
    type = EnumField(AttributeType, by_value=True)
    element_type = EnumField(AttributeElementType, by_value=True)
    numeric_setting = ma.Nested(NewAttributeNumericSettingSchema)
    text_setting = ma.Nested(NewAttributeTextSettingSchema)
    options = ma.Nested(AttributeOptionSchema(many=True))


attribute_schema = AttributeSchema()
attributes_schema = AttributeSchema(many=True)


class NewAttributeDataSchema(masql.SQLAlchemySchema):
    class Meta:
        model = AttributeData

    attribute_id = masql.auto_field()
    data = masql.auto_field()


new_attribute_data_schema = NewAttributeDataSchema()


class NewAttributeOptionDataSchema(masql.SQLAlchemySchema):
    class Meta:
        model = AttributeData

    attribute_id = masql.auto_field()
    option_id = masql.auto_field()


new_attribute_option_data_schema = NewAttributeOptionDataSchema()


class AttributeDataSchema(masql.SQLAlchemySchema):
    class Meta:
        model = AttributeData

    id = masql.auto_field()
    attribute_id = masql.auto_field()
    attribute = ma.Nested(AttributeSchema, many=False)
    option_id = masql.auto_field()
    option = ma.Nested(AttributeOptionSchema(), many=False)
    data = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema)
    created_on = fields.Date()


attribute_data_schema = AttributeDataSchema()
attribute_datum_schema = AttributeDataSchema(many=True)
