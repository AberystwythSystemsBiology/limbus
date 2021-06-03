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


from flask import request, current_app, jsonify, send_file
from ...api import api
from ...api.responses import *
from ...api.filters import generate_base_query_filters, get_filters_and_joins
from ...decorators import token_required
from ...webarg_parser import use_args, use_kwargs, parser

import requests

from ...misc import get_internal_api_header

from marshmallow import ValidationError

from ...database import (
    db,
    UserAccount,
    ColdStorage,
    ColdStorageService,
    DocumentToColdStorage,
)

from ..views import *


@api.route("/storage/coldstorage", methods=["GET"])
@token_required
def storage_coldstorage_home(tokenuser: UserAccount):
    return success_with_content_response(
        basic_cold_storages_schema.dump(ColdStorage.query.all())
    )


@api.route("/storage/coldstorage/LIMBCS-<id>", methods=["GET"])
@token_required
def storage_coldstorage_view(id, tokenuser: UserAccount):
    return success_with_content_response(
        cold_storage_schema.dump(ColdStorage.query.filter_by(id=id).first_or_404())
    )


@api.route("/storage/coldstorage/LIMBCS-<id>/service/new", methods=["POST"])
@token_required
def storage_coldstorage_new_service_report(id, tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    values["storage_id"] = id

    try:
        service_result = new_cold_storage_service_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    csr = ColdStorageService(**values)
    csr.author_id = tokenuser.id

    try:
        db.session.add(csr)
        db.session.commit()

        return success_with_content_response(cold_storage_service_schema.dump(csr))
    except Exception as err:
        return transaction_error_response(err)


@api.route("/storage/coldstorage/new", methods=["POST"])
@token_required
def storage_coldstorage_new(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        cs_result = new_cold_storage_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    cs = ColdStorage(**cs_result)
    cs.author_id = tokenuser.id

    try:
        db.session.add(cs)
        db.session.commit()

        return success_with_content_response(basic_cold_storage_schema.dump(cs))
    except Exception as err:
        return transaction_error_response(err)


@api.route("/storage/coldstorage/LIMBCS-<id>/edit", methods=["PUT"])
@token_required
def storage_coldstorage_edit(id, tokenuser: UserAccount):

    cs = ColdStorage.query.filter_by(id=id).first()

    if not room:
        return not_found()

    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        result = new_cold_storage_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    for attr, value in values.items():
        setattr(cs, attr, value)

    cs.editor_id = tokenuser.id

    try:
        db.session.add(cs)
        db.session.commit()
        db.session.flush()

        return success_with_content_response(basic_cold_storage_schema.dump(cs))
    except Exception as err:
        return transaction_error_response(err)


@api.route("/storage/coldstorage/LIMBCS-<id>/lock", methods=["PUT"])
@token_required
def storage_coldstorage_lock(id, tokenuser: UserAccount):

    cs = ColdStorage.query.filter_by(id=id).first()

    if not cs:
        return not_found()

    cs.is_locked = not cs.is_locked
    cs.editor_id = tokenuser.id

    db.session.add(cs)
    db.session.commit()
    db.session.flush()

    return success_with_content_response(basic_cold_storage_schema.dump(cs))


@api.route("/storage/coldstorage/LIMBCS-<id>/associatie/document", methods=["POST"])
@token_required
def storage_coldstorage_document(id, tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    coldstorage_response = requests.get(
        url_for("api.storage_coldstorage_view", id=id, _external=True),
        headers=get_internal_api_header(tokenuser),
    )

    if coldstorage_response.status_code == 200:
        try:
            values["storage_id"] = id

            cs_result = new_document_to_cold_storage_schema.load(values)
        except ValidationError as err:
            return validation_error_response(err)

        dtcs = DocumentToColdStorage(**cs_result)
        dtcs.author_id = tokenuser.id

        try:
            db.session.add(dtcs)
            db.session.commit()

            return success_with_content_response(
                document_to_cold_storage_schema.dump(dtcs)
            )
        except Exception as err:
            return transaction_error_response(err)

    else:
        return coldstorage_response.json()
