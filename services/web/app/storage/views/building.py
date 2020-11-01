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
from ...database import Building

from ...auth.views import BasicUserAccountSchema


class BasicBuildingSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Building
    
    name = masql.auto_field()

basic_building_schema = BasicBuildingSchema()
basic_buildings_schema = BasicBuildingSchema(many=True)


class NewBuildingSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Building

    name = masql.auto_field()
    site_id = masql.auto_field()

new_building_schema = NewBuildingSchema()