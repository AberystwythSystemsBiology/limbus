from .models import SiteInformation, Address

import marshmallow_sqlalchemy as masql
from marshmallow import fields

class NewAddressSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Address

    id = masql.auto_field()

    street_address_one = masql.auto_field()
    street_address_two = masql.auto_field()
    city = masql.auto_field()
    county = masql.auto_field()
    post_code = masql.auto_field()
    country = masql.auto_field()
