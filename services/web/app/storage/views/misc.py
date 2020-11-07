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
from ...database import SiteInformation, Building, ColdStorage
from ..enums import FixedColdStorageType, FixedColdStorageTemps

class TreeColdStorageSchema(masql.SQLAlchemySchema):
    class Meta:
        model = ColdStorage

    id = masql.auto_field()
    type = EnumField(FixedColdStorageType)
    temp = EnumField(FixedColdStorageTemps)

class TreeBuildingSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Building

    id = masql.auto_field()
    name = masql.auto_field()
    cold_storage = ma.Nested(TreeColdStorageSchema, many=True)

class TreeSiteSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SiteInformation
    
    id = masql.auto_field()
    name = masql.auto_field()
    buildings = ma.Nested(TreeBuildingSchema, many=True)



tree_sites_schema = TreeSiteSchema(many=True)