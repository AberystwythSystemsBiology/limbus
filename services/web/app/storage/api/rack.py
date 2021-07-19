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
from __future__ import print_function

from flask import request, current_app, jsonify, send_file,flash
from ...api import api
from ...api.generics import generic_edit, generic_lock, generic_new
from ...api.responses import *
from ...api.filters import generate_base_query_filters, get_filters_and_joins
from ...decorators import token_required
from ...webarg_parser import use_args, use_kwargs, parser
from ...database import db, SampleRack, UserAccount, EntityToStorage

from ..enums import EntityToStorageType

from sqlalchemy.sql import insert

from marshmallow import ValidationError

from ..views.rack import *
import requests
import sys


@api.route("/storage/rack", methods=["GET"])
@token_required
def storage_rack_home(tokenuser: UserAccount):

    return success_with_content_response(
        basic_sample_racks_schema.dump(SampleRack.query.all())
    )


@api.route("/storage/rack/LIMBRACK-<id>", methods=["GET"])
@token_required
def storage_rack_view(id, tokenuser: UserAccount):
    return success_with_content_response(
        rack_schema.dump(SampleRack.query.filter_by(id=id).first_or_404())
    )


@api.route("/storage/rack/new/", methods=["POST"])
@token_required
def storage_rack_new(tokenuser: UserAccount):
    values = request.get_json()
    return generic_new(
        db,
        SampleRack,
        new_sample_rack_schema,
        basic_sample_rack_schema,
        values,
        tokenuser,
    )


@api.route("/storage/rack/LIMBRACK-<id>/lock", methods=["POST"])
@token_required
def storage_rack_lock(id, tokenuser: UserAccount):
    return generic_lock(db, SampleRack, id, basic_sample_wrack_schema, tokenuser)


@api.route("/storage/rack/LIMBRACK-<id>/edit", methods=["PUT"])
@token_required
def storage_rack_edit(id, tokenuser: UserAccount):
    values = request.get_json()
    return generic_edit(
        db, SampleRack, id, new_sample_rack_schema, rack_schema, values, tokenuser
    )

@api.route("/storage/RACK/LIMBRACK-<id>/delete", methods=["POST"])
@token_required
def storage_rack_delete(id, tokenuser: UserAccount):
    rackTableRecord = SampleRack.query.filter_by(id=id).first()
    entityStorageTableRecord = EntityToStorage.query.filter(EntityToStorage.rack_id==id).all()
    shelfID = entityStorageTableRecord[0].shelf_id

    if not rackTableRecord:
        return not_found()

    if rackTableRecord.is_locked:
        return locked_response()

    rackTableRecord.editor_id = tokenuser.id

    response = func_rack_delete(rackTableRecord,entityStorageTableRecord)
    if response == "success":
        return success_with_content_response(shelfID)
    return sample_assigned_delete_response()

#change to func_rack_delete
def func_rack_delete(record,entityStorageTableRecord):
    for ESRecord in entityStorageTableRecord:
        if not ESRecord.sample_id is None:
            return "has sample"
        db.session.delete(ESRecord)

    try:
        db.session.flush()
        db.session.delete(record)
        db.session.commit()
        return "success"
    except Exception as err:
        return transaction_error_response(err)


@api.route("/storage/rack/assign/sample", methods=["POST"])
@token_required
def storage_transfer_sample_to_rack(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        result = new_sample_to_sample_rack_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    # check if Sample exists.
    ets = EntityToStorage.query.filter_by(sample_id=values["sample_id"]).first()

    if not ets:
        ets = EntityToStorage(**values)
        ets.author_id = tokenuser.id
        ets.storage_type = "STB"
    else:
        ets.shelf_id = None
        ets.rack_id = None
        ets.storage_type = "STB"
        ets.update(values)
    try:
        db.session.add(ets)
        db.session.commit()
        db.session.flush()

        return success_with_content_response(
            view_sample_to_sample_rack_schema.dump(ets)
        )
    except Exception as err:
        print(">>>>>>>>>>>>>>>", err)
        return transaction_error_response(err)
