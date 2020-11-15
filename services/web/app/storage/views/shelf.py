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


from ...extensions import ma
import marshmallow_sqlalchemy as masql
from marshmallow import fields
from marshmallow_enum import EnumField


from ...database import ColdStorageShelf
from ...sample.enums import Colour
from ...sample.views import BasicSampleSchema
from ...auth.views import BasicUserAccountSchema
from ..views.rack import BasicSampleRackSchema

class ColdStorageShelfSchema(masql.SQLAlchemySchema):
    class Meta:
        model = ColdStorageShelf
    
    id = masql.auto_field()
    name = masql.auto_field()
    description = masql.auto_field()
    z = masql.auto_field()
    author = ma.Nested(BasicUserAccountSchema)
    created_on = ma.Date()
    updated_on = ma.Date()
    samples = ma.Nested(BasicSampleSchema, many=True)
    racks = ma.Nested(BasicSampleRackSchema, many=True)
    is_locked = masql.auto_field()
    storage_id = masql.auto_field()
    
shelf_schema = ColdStorageShelfSchema()

class BasicColdStorageShelfSchema(masql.SQLAlchemySchema):
    class Meta:
        model = ColdStorageShelf

    id = masql.auto_field()
    name = masql.auto_field()
    description = masql.auto_field()
    z = masql.auto_field()


basic_shelf_schema = BasicColdStorageShelfSchema()
basic_shelves_schema = BasicColdStorageShelfSchema(many=True)


class ColdStorageShelfSchema(masql.SQLAlchemySchema):
    class Meta:
        model = ColdStorageShelf
    
    id = masql.auto_field()
    name = masql.auto_field()
    description = masql.auto_field()


class NewColdStorageShelfSchema(masql.SQLAlchemySchema):
    class Meta:
        model = ColdStorageShelf

    description = masql.auto_field()
    name = masql.auto_field()
    storage_id = masql.auto_field()


new_shelf_schema = NewColdStorageShelfSchema()
