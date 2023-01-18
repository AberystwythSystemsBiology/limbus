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

from flask import request, current_app, jsonify, send_file, url_for

from ...api import api
from ...api.responses import *
from ...api.filters import generate_base_query_filters, get_filters_and_joins
from ...decorators import token_required, requires_roles
from ...webarg_parser import use_args, use_kwargs, parser
from ...database import db, Building, UserAccount, Room
from ..api.room import func_room_delete


import requests
from ...misc import get_internal_api_header


from marshmallow import ValidationError

from ..views import (
    basic_building_schema,
    basic_buildings_schema,
    new_building_schema,
    building_schema,
)


@api.route("/storage/building/", methods=["GET"])
@token_required
def storage_buildings_home(tokenuser: UserAccount):
    return success_with_content_response(
        basic_buildings_schema.dump(Building.query.all())
    )


@api.route("/storage/building/", methods=["GET"])
@token_required
def storage_buildings_view(tokenuser: UserAccount):
    return success_with_content_response(
        basic_buildings_schema.dump(Building.query.all())
    )


@api.route("/storage/building/LIMBBUILD-<id>", methods=["GET"])
@token_required
def storage_building_view(id, tokenuser: UserAccount):
    return success_with_content_response(
        building_schema.dump(Building.query.filter_by(id=id).first_or_404())
    )


@api.route("/storage/building/new/", methods=["POST"])
@token_required
@requires_roles("data_entry")
def storage_building_new(tokenuser: UserAccount):
    if not tokenuser.has_data_entry_role:
        return not_allowed()

    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        building_result = new_building_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    new_building = Building(**building_result)
    new_building.author_id = tokenuser.id

    try:
        db.session.add(new_building)
        db.session.commit()
        db.session.flush()
        return success_with_content_response(basic_building_schema.dump(new_building))
    except Exception as err:
        return transaction_error_response(err)


@api.route("/storage/building/LIMBBUILD-<id>/lock", methods=["PUT"])
@requires_roles("admin")
def storage_lock_building(id: int, tokenuser: UserAccount):
    building = Building.query.filter_by(id=id).first()

    if not building:
        return not_found()

    building.is_locked = not building.is_locked
    building.editor_id = tokenuser.id

    db.session.commit()
    db.session.flush()

    return success_with_content_response(building.is_locked)


@api.route("/storage/building/LIMBBUILD-<id>/delete", methods=["PUT"])
#@token_required
@requires_roles("data_entry")
def storage_building_delete(id, tokenuser: UserAccount):
    existing = Building.query.filter_by(id=id).first()

    if not existing:
        return not_found()

    if existing.is_locked:
        return locked_response()

    existing.editor_id = tokenuser.id

    code = delete_buildings_func(existing)

    siteID = existing.site_id

    if code == "success":
        return success_with_content_response(siteID)
    elif code == "cold storage":
        return in_use_response(code)
    elif code == "locked":
        return locked_response()
    else:
        return no_values_response()


def delete_buildings_func(record):
    attachedRooms = Room.query.filter(Room.building_id == record.id).all()
    for rooms in attachedRooms:
        code = func_room_delete(rooms)
        if code == "cold storage":
            return "cold storage"
        elif code == "locked" or record.is_locked:
            return "locked"

    try:
        db.session.delete(record)
        db.session.commit()
        return "success"
    except Exception as err:
        return transaction_error_response(err)


@api.route("/storage/building/LIMBBUILD-<id>/edit", methods=["PUT"])
# @token_required
@requires_roles("data_entry")
def storage_edit_building(id: int, tokenuser: UserAccount):
    if not tokenuser.has_data_entry_role:
        return not_allowed()

    building = Building.query.filter_by(id=id).first()

    if not building:
        return not_found()
    if building.is_locked:
        return not_allowed()

    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        result = new_building_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    for attr, value in values.items():
        setattr(building, attr, value)

    building.editor_id = tokenuser.id

    try:
        db.session.add(building)
        db.session.commit()
        db.session.flush()

        return success_with_content_response(basic_building_schema.dump(building))
    except Exception as err:

        return transaction_error_response(err)
