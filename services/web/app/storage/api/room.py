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
from ...database import db, Room, UserAccount

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
@token_required
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
@token_required
def storage_room_edit(id, tokenuser: UserAccount):

    values = request.get_json()

    return generic_edit(
        db, Room, id, new_room_schema, basic_room_schema, values, tokenuser
    )

@api.route("/storage/room/LIMBROOM-<id>/delete", methods=["PUT"])
@token_required
def storage_room_delete(id, tokenuser: UserAccount):

    values = request.get_json()

    return generic_delete(
        db, Room, id, tokenuser
    )

@api.route("/storage/room/LIMBROOM-<id>/lock", methods=["PUT"])
@token_required
def storage_room_lock(id, tokenuser: UserAccount):

    room = Room.query.filter_by(id=id).first()

    if not room:
        return not_found()

    room.is_locked = not room.is_locked
    room.editor_id = tokenuser.id

    db.session.add(room)
    db.session.commit()
    db.session.flush()

    return success_with_content_response(basic_room_schema.dump(room))
