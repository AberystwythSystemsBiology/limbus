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

from .. import ma
from flask import url_for
from .models import Attribute

import marshmallow_sqlalchemy as masql
from marshmallow import fields
from marshmallow_enum import EnumField

from ..auth.views import BasicUserAccountSchema

from .enums import AttributeType, AttributeElementType

class BasicAttributeSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Attribute

    id = masql.auto_field()
    description = masql.auto_field()
    author = ma.Nested(BasicUserAccountSchema)
    created_on = fields.Date()
    type = EnumField(AttributeType)
    element_type = EnumField(AttributeElementType)

basic_attribute_schema = BasicAttributeSchema()
basic_attributes_schema = BasicAttributeSchema(many=True)