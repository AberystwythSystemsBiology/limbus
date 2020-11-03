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
from ...database import db, Building, UserAccount


from marshmallow import ValidationError

from ..views import (
    basic_building_schema,
    basic_buildings_schema,
    new_building_schema
)


@api.route("/storage/building/LIMBUILD-<id>", methods=["GET"])
@token_required
def storage_building_view(id, tokenuser: UserAccount):
    return success_with_content_response(
        basic_building_schema.dump(Building.query.filter_by(id=id).first_or_404())
    )

@api.route("/storage/building/new/", methods=["POST"])
@token_required
def storage_building_new(tokenuser: UserAccount):
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