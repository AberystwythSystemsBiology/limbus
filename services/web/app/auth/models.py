from flask_login import UserMixin
from flask import url_for
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

from .enums import Title

class UserAccount(UserMixin, db.Model):
    __versioned__ = {}
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(320), nullable=False, unique=True)
    title = db.Column(db.Enum(Title), nullable=False)

    first_name = db.Column(db.String(128), nullable=False)
    middle_name = db.Column(db.String(128))
    last_name = db.Column(db.String(128), nullable=False)

    password_hash = db.Column(db.String(256), nullable=False)

    created_on = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        nullable=False
    )

    updated_on = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_bot = db.Column(db.Boolean, default=False, nullable=True)
    is_locked = db.Column(db.Boolean, default=False, nullable=False)

    # TODO: Replace with a site_id
    #address_id = db.Column(db.Integer, db.ForeignKey("addresses.id"), nullable=True)

    @property
    def name(self) -> str:
        return "%s %s" % (self.first_name, self.last_name)

    @property
    def password(self) -> str:
        return "hunter2"

    def get_gravatar(self, size: int = 100) -> str:
        """

        :param size:
        :return:
        """
        if self.is_bot:
            return url_for("static", filename="images/misc/kryten.png")
        else:
            return "https://www.gravatar.com/avatar/%s?s=%i" % (
                hashlib.md5(self.email.encode()).hexdigest(),
                size,
            )

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_authenticated_and_not_bot(self) -> bool:
        False not in [self.is_authenticated, self.is_bot]


@login_manager.user_loader
def load_user(user_id: int) -> UserAccount:
    return UserAccount.query.get(user_id)