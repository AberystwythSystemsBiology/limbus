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
from ...database import db, ColdStorageShelf, UserAccount

from marshmallow import ValidationError
from ..views.shelf import *


@api.route("/storage/shelf", methods=["GET"])
@token_required
def storage_shelf_home(tokenuser: UserAccount):
    return success_with_content_response(
        basic_shelves_schema.dump(ColdStorageShelf.query.all())
    )


@api.route("/storage/shelf/LIMBSHELF-<id>", methods=["GET"])
@token_required
def storage_shelf_view(id, tokenuser: UserAccount):
    return success_with_content_response(
        shelf_schema.dump(
            ColdStorageShelf.query.filter_by(id=id).first_or_404())
    )



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


@api.route("/storage/LIMBSHELF-<id>/lock", methods=["POST"])
@token_required
def storage_shelf_lock(id, tokenuser: UserAccount):
    return generic_lock(db, ColdStorageShelf, id, basic_shelf_schema, tokenuser)