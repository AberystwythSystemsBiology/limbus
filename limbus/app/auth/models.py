from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum

from app import db, login_manager

class TitleType(Enum):
    MR = "Mr."
    MRS = "Mrs."
    MS = "Ms."
    MISS = "Miss."
    M = "M."
    MX = "Mx."
    MASTER = "Master."
    DR = "Dr."
    PROF = "Prof."


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(60), index=True, unique=True)

    title = db.Column(db.Enum(TitleType))

    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)

    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    is_locked = db.Column(db.Boolean, default=False)

    @property
    def password(self) -> AttributeError:
        raise AttributeError("Password is not accessible.")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password) -> bool:
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id: int) -> User:
    return User.query.get(user_id)
