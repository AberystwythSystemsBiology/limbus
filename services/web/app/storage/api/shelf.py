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
from ...api.generics import generic_edit, generic_lock, generic_new
from ...api.responses import *
from ...api.filters import generate_base_query_filters, get_filters_and_joins
from ...decorators import token_required
from ...webarg_parser import use_args, use_kwargs, parser
from ...database import db, UserAccount, EntityToStorage, SampleRack
#from ..api.rack import func_rack_delete
from ...sample.api.base import func_shelf_location

from marshmallow import ValidationError
from ..views.shelf import *
from ..enums import EntityToStorageType


@api.route("/storage/shelf", methods=["GET"])
@token_required
def storage_shelf_home(tokenuser: UserAccount):
    return success_with_content_response(
        basic_shelves_schema.dump(ColdStorageShelf.query.all())
    )


@api.route("/storage/shelf/LIMBSHF-<id>", methods=["GET"])
@token_required
def storage_shelf_view(id, tokenuser: UserAccount):
    # return success_with_content_response(
    #     shelf_schema.dump(ColdStorageShelf.query.filter_by(id=id).first_or_404())
    # )
    shelf = shelf_schema.dump(ColdStorageShelf.query.filter_by(id=id).first_or_404())
    shelf["location"] = func_shelf_location(shelf["id"])["pretty"]
    return success_with_content_response(shelf)


@api.route("/storage/shelf/LIMBSHF-<id>/edit", methods=["PUT"])
@token_required
def storage_shelf_edit(id, tokenuser: UserAccount):
    values = request.get_json()
    print(values)
    return generic_edit(
        db,
        ColdStorageShelf,
        id,
        new_shelf_schema,
        basic_shelf_schema,
        values,
        tokenuser,
    )


@api.route("/storage/shelf/LIMBSHF-<id>/delete", methods=["PUT"])
@token_required
def storage_shelf_delete(id, tokenuser: UserAccount):
    existing = ColdStorageShelf.query.filter_by(id=id).first()

    if not existing:
        return not_found()

    if existing.is_locked:
        return locked_response()

    storageID = existing.storage_id

    entityStorageRecords = EntityToStorage.query.filter(
        EntityToStorage.shelf_id == existing.id
    ).all()

    for ESRecord in entityStorageRecords:
        if ESRecord.storage_type == EntityToStorageType.STS and ESRecord.removed is False:
            return validation_error_response("Can't delete shelf with associated samples")

        elif ESRecord.storage_type == EntityToStorageType.BTS and ESRecord.removed is False:
            return validation_error_response("Can't delete shelf with associated racks")

        #-- Disassociate shelf_id in entitytostorage
        ESRecord.shelf_id = None
        ESRecord.update({"editor_id": tokenuser.id})
        db.session.add(ESRecord)

    try:
        db.session.flush()
        existing.update({"editor_id": tokenuser.id})
        db.session.delete(existing)
        db.session.commit()
        return success_with_content_response(storageID)
    except Exception as err:
        return transaction_error_response(err)


@api.route("/storage/shelf/new/", methods=["POST"])
@token_required
def storage_shelf_new(tokenuser: UserAccount):
    values = request.get_json()
    return generic_new(
        db,
        ColdStorageShelf,
        new_shelf_schema,
        basic_shelf_schema,
        values,
        tokenuser,
    )


@api.route("/storage/LIMBSHF-<id>/lock", methods=["POST"])
@token_required
def storage_shelf_lock(id, tokenuser: UserAccount):
    return generic_lock(db, ColdStorageShelf, id, basic_shelf_schema, tokenuser)
