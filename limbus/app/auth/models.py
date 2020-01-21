from flask_login import UserMixin
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(128), nullable=False, unique=True)

    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    is_locked = db.Column(db.Boolean, default=False)

    @property
    def password(self) -> AttributeError:
        raise AttributeError("Password is not accessible.")

    @property
    def gravatar_hash(self) -> str:
        return hashlib.md5(self.email.encode()).hexdigest()

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password) -> bool:
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id: int) -> User:
    return User.query.get(user_id)
