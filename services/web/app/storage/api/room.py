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

from flask import request, current_app, jsonify, send_file, url_for, redirect

from ...api import api
from ...api.responses import *
from ...api.filters import generate_base_query_filters, get_filters_and_joins
from ...decorators import token_required, requires_roles
from ...webarg_parser import use_args, use_kwargs, parser
from ...database import db, Room, UserAccount, ColdStorage
import requests
from .lts import storage_coldstorage_delete
from ...misc import get_internal_api_header
from ..api.lts import delete_coldstorage_func


from marshmallow import ValidationError

from ..views import basic_room_schema, basic_rooms_schema, new_room_schema, room_schema
from ...api.generics import *


@api.route("/storage/room", methods=["GET"])
@token_required
def storage_room_home(tokenuser: UserAccount):
    return success_with_content_response(basic_rooms_schema.dump(Room.query.all()))


@api.route("/storage/room/LIMBROOM-<id>", methods=["GET"])
@token_required
def storage_room_view(id, tokenuser: UserAccount):
    return success_with_content_response(
        room_schema.dump(Room.query.filter_by(id=id).first_or_404())
    )


@api.route("/storage/room/new", methods=["POST"])
# @token_required
@requires_roles("data_entry")
def storage_room_new(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        room_result = new_room_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    room = Room(**room_result)
    room.author_id = tokenuser.id

    try:
        db.session.add(room)
        db.session.commit()

        return success_with_content_response(basic_room_schema.dump(room))
    except Exception as err:
        return transaction_error_response(err)


@api.route("/storage/room/LIMBROOM-<id>/edit", methods=["PUT"])
# @token_required
@requires_roles("data_entry")
def storage_room_edit(id, tokenuser: UserAccount):
    values = request.get_json()

    return generic_edit(
        db, Room, id, new_room_schema, basic_room_schema, values, tokenuser
    )


# *
# Route for deleting a room
# *
@api.route("/storage/room/LIMBROOM-<id>/delete", methods=["PUT"])
# @token_required
@requires_roles("data_entry")
def storage_room_delete(id, tokenuser: UserAccount):
    existing = Room.query.filter_by(id=id).first()

    if not existing:
        return not_found()

    if existing.is_locked:
        return locked_response()

    existing.editor_id = tokenuser.id

    buildingID = existing.building_id

    code = func_room_delete(existing)

    # Type of error
    if code == "success":
        return success_with_content_response(buildingID)
    elif code == "cold storage":
        return in_use_response(code)
    elif code == "locked":
        return locked_response()
    else:
        return no_values_response()


# *
# Deletes the room passed in.
# Includes validation for deleting.
# *
def func_room_delete(record):
    attachedCS = ColdStorage.query.filter(ColdStorage.room_id == record.id).first()
    if not attachedCS is None:
        return "cold storage"
    if record.is_locked:
        return "locked"
    try:
        db.session.delete(record)
        db.session.commit()
        return "success"
    except Exception as err:
        return transaction_error_response(err)


# *
# Function changes the state of the lock variable for the room.
# Locking a room reduces the functionality to the user.
# *
@api.route("/storage/room/LIMBROOM-<id>/lock", methods=["PUT"])
# @token_required
@requires_roles("data_entry")
def storage_room_lock(id, tokenuser: UserAccount):
    room = Room.query.filter_by(id=id).first()

    if not room:
        return not_found()

    # Updates the attribute
    if room.is_locked:
        room.is_locked = False
    else:
        room.is_locked = True
    room.editor_id = tokenuser.id

    try:
        db.session.commit()
        db.session.flush()
        return success_with_content_response(room.is_locked)
    except Exception as err:
        return transaction_error_response(err)
