from ..api import (
    api,
    no_values_response,
    sql_error_response,
    validation_error_response,
    success_without_content_response,
    success_with_content_response,
)

from .. import db, spec
from flask import request, current_app, jsonify
from ..decorators import tbasic_user_accounts_schemaoken_required

from marshmallow import ValidationError
import json
from .views import (
    new_user_account_schema,
    basic_user_accounts_schema,
    full_user_account_schema,
)

from .models import UserAccount


@api.route("/auth")
@token_required
def auth_home(tokenuser: UserAccount):
    return success_with_content_response(
        basic_user_accounts_schema.dump(UserAccount.query.all())
    )


@api.route("/auth/user/<id>", methods=["GET"])
@token_required
def auth_view_user(id: int, tokenuser: UserAccount):
    # TODO: Check if admin or if the current user id == id.
    return success_with_content_response(
        full_user_account_schema.dump(UserAccount.query.filter_by(id=id).first())
    )


@api.route("/auth/user/new", methods=["POST"])
@token_required
def auth_new_user(tokenuser: UserAccount) -> dict:
    """A cute furry animal endpoint.
    ---
    post:str
      description: Get a random pet
      responses:
        200:
          content:
            application/json:
              schema: FullUserAccountSchema
    """

    values = request.get_json()
    try:
        result = new_user_account_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    new_user_account = UserAccount(**result)
    new_user_account.created_by = tokenuser.id

    try:
        db.session.add(new_user_account)
        db.session.commit()
        db.session.flush()
        return success_with_content_response(
            basic_user_accounts_schema.dump(new_user_account)
        )
    except Exception as err:
        return sql_error_response(err)
