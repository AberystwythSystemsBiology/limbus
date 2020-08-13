# Copyright (C) 2019  Keiron O'Shea <keo7@aber.ac.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from flask import request

from ..decorators import token_required
from ..api import api
from ..api.responses import *
from ..api.filters import generate_base_query_filters, get_filters_and_joins
from marshmallow import ValidationError


from .views import (
    stores_schema,
    store_schema,
    StoreSearchSchema,
    new_store_schema,
    store_update_schema
)

from ..database import db, UserAccount, TemporaryStore

from ..webarg_parser import use_args, use_kwargs, parser
from uuid import uuid4


@api.route("tmpstore/")
@token_required
def tmpstore_home(tokenuser: UserAccount):
    filters, allowed = generate_base_query_filters(tokenuser, "view")

    if not allowed:
        return not_allowed()

    return success_with_content_response(stores_schema.dump(TemporaryStore.query.filter_by(**filters).all()))

@api.route("/tmpstore/<hash>")
@token_required
def tmpstore_view_tmpstore(hash: str, tokenuser: UserAccount):
    return success_with_content_response(
        store_schema.dump(TemporaryStore.query.filter_by(hash=hash).first())
    )

@api.route("/tmpstore/query", methods=["GET"])
@use_args(StoreSearchSchema(), location="json")
@token_required
def tmpstore_query(args, tokenuser: UserAccount):
    filters, joins = get_filters_and_joins(args, TemporaryStore)

    return success_with_content_response(
        stores_schema.dump(
            TemporaryStore.query.filter_by(**filters).filter(*joins).all())
    )

@api.route("/tmpstore/new", methods=["POST"])
@token_required
def tmpstore_new_tmpstore(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    values["uuid"] = uuid4()

    try:
        result = new_store_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    new_tmpstore = TemporaryStore(**result)
    new_tmpstore.author_id = tokenuser.id

    try:
        db.session.add(new_tmpstore)
        db.session.commit()
        db.session.flush()
        return success_with_content_response(store_schema.dump(new_tmpstore))
    except Exception as err:
        return transaction_error_response(err)

@api.route("/tmpstore/<hash>/delete", methods=["DELETE"])
@token_required
def tmpstore_remove_tmpstore(hash: str, tokenuser: UserAccount):
    pass

@api.route("/tmpstore/<hash>/edit", methods=["PUT"])
@token_required
def tmpstore_edit_tmpstore(hash, tokenuser:UserAccount):
    tmpstore = TemporaryStore.query.filter_by(uuid=hash).first()

    if not tmpstore:
        return not_found()

    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        result = store_update_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    tmpstore.data = values["data"]

    tmpstore.editor_id = tokenuser.id

    try:
        db.session.add(tmpstore)
        db.session.commit()
        db.session.flush()

        return success_with_content_response(store_schema.dump(tmpstore))
    except ValidationError as err:
        return validation_error_response(err)
