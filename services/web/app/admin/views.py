from .routes import db
from ..auth.models import User
from ..auth.views import UserView


def UserAccountsView() -> dict:
    users = db.session.query(User).filter().all()

    data = {}

    for user in users:
        data[user.id] = UserView(user.id)

    return data
