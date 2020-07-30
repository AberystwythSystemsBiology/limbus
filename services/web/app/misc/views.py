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

from .models import SiteInformation, Address

import marshmallow_sqlalchemy as masql
from marshmallow import fields
from .. import ma

from ..auth.views import BasicUserAccountSchema


class NewAddressSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Address

    street_address_one = masql.auto_field()
    street_address_two = masql.auto_field()
    city = masql.auto_field()
    county = masql.auto_field()
    post_code = masql.auto_field()
    country = masql.auto_field()
    author_id = masql.auto_field()


new_address_schema = NewAddressSchema()


class BasicAddressSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Address

    id = masql.auto_field()
    street_address_one = masql.auto_field()
    street_address_two = masql.auto_field()
    city = masql.auto_field()
    county = masql.auto_field()
    post_code = masql.auto_field()
    country = masql.auto_field()

basic_address_schema = BasicAddressSchema()
basic_addresses_schema = BasicAddressSchema(many=True)


class NewSiteInformationSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SiteInformation

    miabis_id = masql.auto_field()
    acronym = masql.auto_field()
    name = masql.auto_field()
    description = masql.auto_field()
    url = masql.auto_field()
    author_id = masql.auto_field()
    address_id = masql.auto_field()


new_site_schema = NewSiteInformationSchema()

class BasicSiteSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SiteInformation
    
    id = masql.auto_field()
    miabis_id = masql.auto_field()
    acronym = masql.auto_field()
    name = masql.auto_field()
    description = masql.auto_field()
    url = masql.auto_field()
    address = ma.Nested(BasicAddressSchema)

basic_site_schema = BasicSiteSchema()
basic_sites_schema = BasicSiteSchema(many=True)