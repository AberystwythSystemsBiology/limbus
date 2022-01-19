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

from flask_login import UserMixin
from flask import url_for
from werkzeug.security import generate_password_hash, check_password_hash
from ..database import db, Base
import hashlib

from .enums import Title, AccountType, AccessControl
from sqlalchemy.dialects.postgresql import JSONB


class UserAccount(Base, UserMixin):
    __versioned__ = {}

    created_on = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_on = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    email = db.Column(db.String(320), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)

    title = db.Column(db.Enum(Title), nullable=False)
    first_name = db.Column(db.String(128), nullable=False)
    middle_name = db.Column(db.String(128))
    last_name = db.Column(db.String(128), nullable=False)

    account_type = db.Column(db.Enum(AccountType), nullable=False)
    access_control = db.Column(db.Enum(AccessControl), nullable=True)

    token = db.relationship("UserAccountToken", uselist=False)

    site_id = db.Column(
        db.Integer, db.ForeignKey("siteinformation.id", use_alter=True), nullable=True
    )
    site = db.relationship(
        "SiteInformation",
        primaryjoin="UserAccount.site_id==SiteInformation.id",
        uselist=False,
    )

    settings = db.Column(JSONB, nullable=True)

    @property
    def password(self) -> str:
        return "hunter2"

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_bot(self) -> bool:
        return self.account_type == AccountType.BOT

    @property
    def is_admin(self) -> bool:
        return self.account_type == AccountType.ADM

    @property
    def is_authenticated_and_not_bot(self) -> bool:
        return [self.is_authenticated, self.is_bot]

    def get_gravatar(self, size: int = 100) -> str:
        if self.account_type == "BOT":
            return url_for("static", filename="images/misc/kryten.png")
        else:
            return "https://www.gravatar.com/avatar/%s?s=%i" % (
                hashlib.md5(self.email.encode()).hexdigest(),
                20,
            )


class UserAccountPasswordResetToken(Base):
    created_on = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_on = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    user_id = db.Column(
        db.Integer, db.ForeignKey("useraccount.id", use_alter=True), nullable=False
    )

    token = db.Column(db.String(256), nullable=False)


class UserAccountToken(Base):

    user_id = db.Column(
        db.Integer, db.ForeignKey("useraccount.id", use_alter=True), nullable=False
    )
    token_hash = db.Column(db.String(256), nullable=False)

    @property
    def token(self) -> str:
        return "*******"

    @token.setter
    def token(self, token: str):
        self.token_hash = generate_password_hash(token)

    def verify_token(self, token) -> bool:
        return check_password_hash(self.token_hash, token)
