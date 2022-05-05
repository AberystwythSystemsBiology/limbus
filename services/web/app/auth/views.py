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

from ..extensions import ma
from flask import url_for
import hashlib
from .models import UserAccount, UserAccountToken
from .enums import AccountType, Title, AccessControl

import marshmallow_sqlalchemy as masql
from marshmallow import fields
from marshmallow_enum import EnumField


class UserAccountSearchSchema(masql.SQLAlchemySchema):
    class Meta:
        model = UserAccount

    id = masql.auto_field()
    email = masql.auto_field()
    first_name = masql.auto_field()
    last_name = masql.auto_field()


user_account_search_schema = UserAccountSearchSchema()
user_accounts_search_schema = UserAccountSearchSchema(many=True)


class UserAccountSettingSchema(masql.SQLAlchemySchema):
    class Meta:
        model = UserAccount

    id = masql.auto_field()
    email = masql.auto_field()
    first_name = masql.auto_field()
    last_name = masql.auto_field()
    site_id = masql.auto_field()
    settings = masql.auto_field()


user_account_setting_schema = UserAccountSettingSchema()
user_accounts_setting_schema = UserAccountSettingSchema(many=True)


class BasicUserAccountSchema(masql.SQLAlchemySchema):
    class Meta:
        model = UserAccount

    id = masql.auto_field()
    email = masql.auto_field()

    first_name = masql.auto_field()
    last_name = masql.auto_field()

    account_type = EnumField(AccountType, by_value=True)

    created_on = ma.Date()

    is_locked = masql.auto_field()
    site_id = masql.auto_field()
    settings = masql.auto_field()

    gravatar = fields.Method("get_gravatar")

    def get_gravatar(self, user):
        if user.account_type == "BOT":
            return url_for("static", filename="images/misc/kryten.png")
        else:
            return "https://www.gravatar.com/avatar/%s?s=%i" % (
                hashlib.md5(user.email.encode()).hexdigest(),
                20,
            )


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
    settings = masql.auto_field()

    site_id = masql.auto_field()

    password = fields.Str(required=True)


new_user_account_schema = NewUserAccountSchema()


class EditUserAccountSchema(masql.SQLAlchemySchema):
    class Meta:
        model = UserAccount

    title = masql.auto_field(required=False)
    first_name = masql.auto_field(required=False)
    middle_name = masql.auto_field(required=False)
    last_name = masql.auto_field(required=False)
    settings = masql.auto_field()


edit_user_account_schema = EditUserAccountSchema()

from ..misc.views import basic_site_schema


class AdminEditUserAccountSchema(masql.SQLAlchemySchema):
    class Meta:
        model = UserAccount

    is_locked = masql.auto_field(required=False)
    email = masql.auto_field(required=False)
    title = masql.auto_field(required=False)
    first_name = masql.auto_field(required=False)
    middle_name = masql.auto_field(required=False)
    last_name = masql.auto_field(required=False)

    account_type = masql.auto_field(required=False)
    access_control = masql.auto_field(required=False)
    settings = masql.auto_field(required=False)
    site_id = masql.auto_field(required=False)


admin_edit_user_account_schema = AdminEditUserAccountSchema()


class PasswordResetFormSchema(masql.SQLAlchemySchema):
    class Meta:
        model = UserAccount

    email = masql.auto_field(required=True)


password_reset_form_schema = PasswordResetFormSchema()


class TokenSchema(masql.SQLAlchemySchema):
    class Meta:
        model = UserAccountToken

    created_on = fields.Date()
    updated_on = fields.Date()


from ..document.views import BasicDocumentSchema


class FullUserAccountSchema(masql.SQLAlchemySchema):
    class Meta:
        model = UserAccount

    id = masql.auto_field()

    title = EnumField(Title)  # , by_value=True)

    email = masql.auto_field()
    first_name = masql.auto_field()
    middle_name = masql.auto_field()
    last_name = masql.auto_field()

    account_type = EnumField(AccountType, by_value=True)
    access_control = EnumField(AccessControl, by_value=True)

    settings = masql.auto_field()

    created_on = fields.Date()
    updated_on = fields.Date()

    token = ma.Nested(TokenSchema())
    is_locked = masql.auto_field()

    site = ma.Nested(basic_site_schema)
    document = ma.Nested(BasicDocumentSchema)

    _links = ma.Hyperlinks({"self": ma.URLFor("api.auth_view_user", id="<id>")})

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
