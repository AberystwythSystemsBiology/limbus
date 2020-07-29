from .. import db, ma
from .models import UserAccount
from .enums import AccountType, Title, AccessControl

import marshmallow_sqlalchemy as masql
from marshmallow import fields
from marshmallow_enum import EnumField



class BasicUserAccountSchema(masql.SQLAlchemySchema):
    class Meta:
        model = UserAccount

    id = masql.auto_field()
    email = masql.auto_field()


basic_user_account_schema = BasicUserAccountSchema()
basic_user_accounts_schema = BasicUserAccountSchema(many=True)


class NewUserAccountSchema(masql.SQLAlchemySchema):
    class Meta:
        model = UserAccount

    email = masql.auto_field()
    title = masql.auto_field()
    first_name = masql.auto_field()
    middle_name = masql.auto_field()
    last_name = masql.auto_field()

    account_type = masql.auto_field()
    access_control = masql.auto_field()

    site_id = masql.auto_field()

    password = fields.Str(required=True)


new_user_account_schema = NewUserAccountSchema()


from ..misc.views import basic_site_schema

class FullUserAccountSchema(masql.SQLAlchemySchema):
    class Meta:
        model = UserAccount
    title = EnumField(Title)

    email = masql.auto_field()
    first_name = masql.auto_field()
    middle_name = masql.auto_field()
    last_name = masql.auto_field()

    account_type = EnumField(AccountType)
    access_control = EnumField(AccessControl)

    created_on = masql.auto_field()

    site = ma.Nested(basic_site_schema)

full_user_account_schema = FullUserAccountSchema()
full_user_accounts_schema = FullUserAccountSchema(many=True)
