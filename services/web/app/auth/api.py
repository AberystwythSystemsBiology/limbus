from . import auth
from .. import db
from flask import request
from ..decorators import token_required

from marshmallow import ValidationError
import json
from .views import basic_user_accounts_schema, full_user_account_schema
from .models import UserAccount

@auth.route("/api")
@token_required
def api_home(tokenuser: UserAccount):
    return {"results": basic_user_accounts_schema.dump(UserAccount.query.all())}

@auth.route("/api/user/<id>", methods=["GET"])
@token_required
def api_view_user(id: int, tokenuser: UserAccount):
    # TODO: Check if admin or if the current user id == id.
    return full_user_account_schema.dump(UserAccount.query.filter_by(id=id).first())

@auth.route("/api/user/new", methods=["POST"])
@token_required
def api_new_user(tokenuser: UserAccount) -> dict:
    """

    :param tokenuser:
    :return:
    """

    json_data = request.get_json()

    if not json_data:
        return {"message": "No input data provided"}, 400

    try:
        result = full_user_account_schema.load(json_data)

        new_user_account = UserAccount(**result)
        new_user_account.created_by = tokenuser.id
        db.session.add(new_user_account)

        try:
            db.session.commit()
            db.session.flush()
            return {"success": True}, 200

        except Exception as err:
            return {"success": False, "message": str(err.orig.diag.message_primary)}, 400

    except ValidationError as err:
        return {"success": False, "messages" : err.messages}, 400


