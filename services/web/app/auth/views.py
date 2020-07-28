from .. import db, ma
from .models import UserAccount

import marshmallow_sqlalchemy as masql
from marshmallow import fields


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

    password = fields.Str(required=True)


new_user_account_schema = NewUserAccountSchema()

class FullUserAccountSchema(masql.SQLAlchemySchema):
    class Meta:
        model = UserAccount

    email = masql.auto_field()
    title = masql.auto_field()
    first_name = masql.auto_field()
    middle_name = masql.auto_field()
    last_name = masql.auto_field()

    account_type = masql.auto_field()
    access_control = masql.auto_field()

full_user_account_schema = FullUserAccountSchema()
full_user_accounts_schema = FullUserAccountSchema(many=True)