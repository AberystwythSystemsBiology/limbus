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