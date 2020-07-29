from .. import db, ma
from flask import url_for
import hashlib
from .models import UserAccount, UserAccountToken
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

class EditUserAccountSchema(masql.SQLAlchemySchema):
    class Meta:
        model = UserAccount

    title = masql.auto_field()
    first_name = masql.auto_field()
    middle_name = masql.auto_field()
    last_name = masql.auto_field()

edit_user_account_schema = EditUserAccountSchema()

from ..misc.views import basic_site_schema

class TokenSchema(masql.SQLAlchemySchema):
    class Meta:
        model = UserAccountToken
    created_on = fields.Date()
    updated_on = fields.Date()

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

    created_on = fields.Date()
    updated_on = fields.Date()

    token = ma.Nested(TokenSchema())

    site = ma.Nested(basic_site_schema)

    _links = ma.Hyperlinks({
        'self': ma.URLFor('api.auth_view_user', id='<id>')
    })

    gravatar = fields.Method("get_gravatar")

    def get_gravatar(self, user):
        if user.account_type == "BOT":
            return url_for("static", filename="images/misc/kryten.png")
        else:
            return "https://www.gravatar.com/avatar/%s?s=%i" % (
                hashlib.md5(user.email.encode()).hexdigest(),
                200,
            )


full_user_account_schema = FullUserAccountSchema()
full_user_accounts_schema = FullUserAccountSchema(many=True)
