from .routes import db
from ..auth.models import User, Profile
from ..auth.views import UserView


def UserAccountsView() -> dict:
    users = db.session.query(User, Profile).filter(User.profile_id == Profile.id).all()

    data = {}

    for user, profile in users:
        data[user.id] = UserView(user.id, [user, profile])

    return data
