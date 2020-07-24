from . import auth
from .. import db
from flask import request
from flask_login import login_required, current_user

from ..decorators import token_required

from .views import basic_user_accounts_schema, full_user_account_schema
from .models import UserAccount

@auth.route("/api")
@token_required
def api_home(tokenuser: UserAccount):
    print(tokenuser)
    return {"results": basic_user_accounts_schema.dump(UserAccount.query.all())}

@auth.route("/api/user/<id>", methods=["GET"])
def api_view_user(id: int):
    # TODO: Check if admin or if the current user id == id.
    return full_user_account_schema.dump(UserAccount.query.filter_by(id=id).first())

@auth.route("/api/user/new", methods=["POST"])
def api_new_user(current_user_from_decorator: UserAccount):

    json_data = request.get_json()

    if not json_data:
        return {"message": "No input data provided"}, 400

    # TODO: Write validators.
    new_user_account = UserAccount(**json_data)

    new_user_account.created_by = current_user_from_decorator.id
    db.session.add(new_user_account)
    db.session.commit()
    db.session.flush()

    return {"success": True, "id":  full_user_account_schema.dump(new_user_account)}, 200