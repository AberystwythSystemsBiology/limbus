from ..api import api
from ..api.responses import *

from .. import db, spec
from flask import request, current_app, jsonify
from ..decorators import token_required

from marshmallow import ValidationError
import json
from .views import (
    new_user_account_schema,
    basic_user_account_schema,
    basic_user_accounts_schema,
    full_user_account_schema,
    edit_user_account_schema,
)

from .models import UserAccount


@api.route("/auth")
@token_required
def auth_home(tokenuser: UserAccount):
    return success_with_content_response(
        basic_user_accounts_schema.dump(UserAccount.query.all())
    )


@api.route("/auth/user/<id>", methods=["GET"])
def auth_view_user(id: int):
    # TODO: Check if admin or if the current user id == id.
    return success_with_content_response(
        full_user_account_schema.dump(UserAccount.query.filter_by(id=id).first())
    )


@api.route("/auth/user/<id>/edit", methods=["PUT"])
@token_required
def auth_edit_user(id: int, tokenuser: UserAccount) :
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        result = edit_user_account_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    user = UserAccount.query.filter_by(id = id).first()

    for attr, value in values.items():
        setattr(user, attr, value)

    try:
        db.session.add(user)
        db.session.commit()
        db.session.flush()
        return success_with_content_response(
            basic_user_account_schema.dump(user)
        )
    except Exception as err:
        return transaction_error_response(err)


@api.route("/auth/user/new", methods=["POST"])
@token_required
def auth_new_user(tokenuser: UserAccount) -> dict:

    values = request.get_json()

    if not values:
        return no_values_response()

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
            basic_user_account_schema.dump(new_user_account)
        )
    except Exception as err:
        return transaction_error_response(err)
