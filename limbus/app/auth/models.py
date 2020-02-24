from flask_login import UserMixin
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager

from .enums import Title


class User(UserMixin, db.Model):
    __versioned__ = {}
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(128), nullable=False, unique=True)

    password_hash = db.Column(db.String(128))

    profile_id = db.Column(db.Integer, db.ForeignKey("profiles.id"))

    is_admin = db.Column(db.Boolean, default=False)
    is_locked = db.Column(db.Boolean, default=False)

    creation_date = db.Column(db.DateTime,
                              server_default=db.func.now(),
                              nullable=False)
    update_date = db.Column(db.DateTime,
                            server_default=db.func.now(),
                            server_onupdate=db.func.now(),
                            nullable=False)

    @property
    def password(self) -> AttributeError:
        raise AttributeError("Password is not accessible.")

    @property
    def gravatar(self) -> str:
        return hashlib.md5(self.email.encode()).hexdigest()

    @property
    def name(self) -> str:
        ptu = db.session.query(ProfileToUser).filter(
            ProfileToUser.user_id == self.id).first_or_404()
        profile = db.session.query(Profile).filter(
            Profile.id == ptu.id).first()
        return "%s %s" % (profile.first_name, profile.last_name)

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password) -> bool:
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id: int) -> User:
    return User.query.get(user_id)


class Profile(db.Model):

    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.Enum(Title), nullable=False)
    first_name = db.Column(db.String(128))
    middle_name = db.Column(db.String(128))
    last_name = db.Column(db.String(128))

    creation_date = db.Column(db.DateTime,
                              server_default=db.func.now(),
                              nullable=False)
    update_date = db.Column(db.DateTime,
                            server_default=db.func.now(),
                            server_onupdate=db.func.now(),
                            nullable=False)


class ProfileToUser(db.Model):
    __tablename__ = "profiles_to_users"

    id = db.Column(db.Integer, primary_key=True)

    profile_id = db.Column(db.Integer, db.ForeignKey("profiles.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))


class ProfileToAddress(db.Model):
    __versioned__ = {}
    __tablename__ = "profiles_to_addresses"
    id = db.Column(db.Integer, primary_key=True)

    profile_id = db.Column(db.Integer, db.ForeignKey("profiles.id"))
    address = db.Column(db.Integer, db.ForeignKey("addresses.id"))

    creation_date = db.Column(db.DateTime,
                              server_default=db.func.now(),
                              nullable=False)
    update_date = db.Column(db.DateTime,
                            server_default=db.func.now(),
                            server_onupdate=db.func.now(),
                            nullable=False)


class ProfileToBiobank(db.Model):
    __versioned__ = {}
    __tablename__ = "profiles_to_biobanks"

    id = db.Column(db.Integer, primary_key=True)

    creation_date = db.Column(db.DateTime,
                              server_default=db.func.now(),
                              nullable=False)
    update_date = db.Column(db.DateTime,
                            server_default=db.func.now(),
                            server_onupdate=db.func.now(),
                            nullable=False)
