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
from sqlalchemy import func
from ...api import api
from ...api.responses import *
from ...api.filters import generate_base_query_filters, get_filters_and_joins
from ...decorators import token_required
from ...webarg_parser import use_args, use_kwargs, parser
from ...database import *

from marshmallow import ValidationError

from ..views.misc import (
    tree_sites_schema,
    new_sample_to_sample_rack_schema,
    new_sample_to_shelf_schema,
    new_sample_rack_to_shelf_schema,
)


@api.route("/storage/transfer/rack_to_shelf", methods=["POST"])
@token_required
def storage_transfer_rack_to_shelf(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        rack_to_shelf_result = new_sample_rack_to_shelf_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    ets = EntityToStorage.query.filter_by(rack_id=values["rack_id"], storage_type='BTS').first()

    if ets is not None:
        ets.box_id = None
        ets.shelf_id = values["shelf_id"]
        ets.editor_id = tokenuser.id
        ets.storage_type = "BTS"

    else:
        ets = EntityToStorage(**rack_to_shelf_result)
        ets.author_id = tokenuser.id
        ets.storage_type = "BTS"
        db.session.add(ets)

    try:
        db.session.commit()
        return success_with_content_response({"success": True})
    except Exception as err:
        return transaction_error_response(err)


@api.route("/storage/transfer/sample_to_shelf", methods=["POST"])
@token_required
def storage_transfer_sample_to_shelf(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        sample_to_shelf_result = new_sample_to_shelf_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    ets = EntityToStorage.query.filter_by(sample_id=values["sample_id"], storage_type='STB').first()
    if ets != None:
        # warning, confirmation
        db.session.delete(ets)

    ets = EntityToStorage.query.filter_by(sample_id=values["sample_id"], storage_type='STS').first()
    if ets != None:
        ets.box_id = None
        ets.shelf_id = values["shelf_id"]
        ets.editor_id = tokenuser.id
        ets.updated_on = func.now()
        ets.storage_type = "STS"

    else:
        ets = EntityToStorage(
            sample_id=values["sample_id"],
            shelf_id=values["shelf_id"],
            storage_type="STS",
            entry=values["entry"],
            entry_datetime=values["entry_datetime"],
            author_id=tokenuser.id,
        )

    try:
        db.session.add(ets)
        db.session.commit()
        return success_with_content_response({"success": True})
    except Exception as err:
        return transaction_error_response(err)


@api.route("/storage/tree", methods=["GET"])
@token_required
def storage_view_tree(tokenuser: UserAccount):

    return success_with_content_response(
        tree_sites_schema.dump(SiteInformation.query.all())
    )


@api.route("/storage", methods=["GET"])
@token_required
def storage_view_panel(tokenuser: UserAccount):

    data = {
        "basic_statistics": {
            "site_count": SiteInformation.query.count(),
            "building_count": Building.query.count(),
            "room_count": Room.query.count(),
            "cold_storage_count": ColdStorage.query.count(),
        },
        "cold_storage_statistics": {
            "cold_storage_type": prepare_for_chart_js(
                [
                    (type.value, count)
                    for (type, count) in db.session.query(
                        ColdStorage.type, func.count(ColdStorage.type)
                    )
                    .group_by(ColdStorage.type)
                    .all()
                ]
            ),
            "cold_storage_temp": prepare_for_chart_js(
                [
                    (type.value, count)
                    for (type, count) in db.session.query(
                        ColdStorage.temp, func.count(ColdStorage.temp)
                    )
                    .group_by(ColdStorage.temp)
                    .all()
                ]
            ),
        },
    }

    return success_with_content_response(data)
