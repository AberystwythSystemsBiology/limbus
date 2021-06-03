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

from ...database import SiteInformation
from .building import BasicBuildingSchema
from ...database import db, Address, SiteInformation, UserAccount, Sample

from ...auth.views import BasicUserAccountSchema
from ...misc.views import BasicAddressSchema

from ...extensions import ma
import marshmallow_sqlalchemy as masql
from marshmallow import fields
from marshmallow_enum import EnumField


class SiteSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SiteInformation

    id = masql.auto_field()
    miabis_id = masql.auto_field()
    acronym = masql.auto_field()
    name = masql.auto_field()
    description = masql.auto_field()
    url = masql.auto_field()
    address = ma.Nested(BasicAddressSchema)
    buildings = ma.Nested(BasicBuildingSchema, many=True)

    author = ma.Nested(BasicUserAccountSchema)


site_schema = SiteSchema()
sites_schema = SiteSchema(many=True)
