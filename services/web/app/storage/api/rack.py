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
from ...database import db, SampleRack, UserAccount, EntityToStorage

from marshmallow import ValidationError

from ..views.rack import *
import requests


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
def storage_rack_edit(id, tokenuser:UserAccount):
    values = request.get_json()
    return generic_edit(db, SampleRack, id, new_sample_rack_schema, rack_schema, values, tokenuser)

@api.route("/storage/rack/LIMBRACK-<id>/assign_sample", methods=["POST"])
@token_required
def storage_rack_add_sample(id, tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        result = new_sample_to_sample_rack_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    # check if Sample exists.
    existing = EntityToStorage.query.filter_by(sample_id=values["sample_id"]).first()

    if not existing:
        new = EntityToStorage(**values)
        new.author_id = tokenuser.id
        db.session.add(new)
    else:
        existing.shelf_id = None
        existing.rack_id = None

        existing.update(values)
        db.session.add(existing)
    
    try:
        db.session.commit()
        db.session.flush()

        return success_with_content_response(view_sample_to_sample_rack_schema.dump(existing))
    except Exception as err:
        return transaction_error_response(err)
    
