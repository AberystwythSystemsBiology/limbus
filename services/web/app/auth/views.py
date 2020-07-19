from .. import db
from .models import UserAccount

import marshmallow_sqlalchemy as ma

class BasicUserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = UserAccount

    email = ma.auto_field()

basic_user_schema = BasicUserSchema()
basic_users_schema = BasicUserSchema(many=True)



def UserIndexView() -> dict:
    users = db.session.query(UserAccount).all()

    data = {}

    for user in users:
        data[user.id] = {
            "email": user.email,
            "is_admin": user.is_admin,
            "is_locked": user.is_locked,
            "name": user.name,
            "creation_date": user.creation_date,
            "update_date": user.update_date,
        }

    return data


def UserView(id: int, user_profile: list = None) -> dict:
    return { }
