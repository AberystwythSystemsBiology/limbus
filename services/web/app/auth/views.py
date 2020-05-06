from .. import db
from .models import User, Profile

def UserIndexView() -> dict:
    users = db.session.query(User).all()

    data = {}

    for user in users:
        data[user.id] = {
            "email": user.email,
            "is_admin": user.is_admin,
            "is_locked": user.is_locked,
            "name": user.name,
            "creation_date": user.creation_date,
            "update_date": user.update_date
        }

    return data


def UserView(id: int, user_profile: list = None) -> dict:

    if user_profile == None:
        user, profile = db.session.query(
            User,
            Profile
        ).filter(User.id == id).filter(Profile.id == User.profile_id).first_or_404()
    else:
        user, profile = user_profile

    return {
        "id": user.id,
        "email": user.email,
        "is_admin": user.is_admin,
        "is_locked": user.is_locked,
        "creation_date": user.creation_date,
        "update_date": user.update_date,
        "gravatar": user.gravatar(),
        "profile" : {
            "id": profile.id,
            "title": profile.title,
            "first_name": profile.first_name,
            "middle_name": profile.middle_name,
            "last_name": profile.last_name,
            "creation_date": profile.creation_date,
            "update_date": profile.update_date
        }

    }