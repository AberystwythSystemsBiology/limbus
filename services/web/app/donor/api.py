# Copyright (C) 2019  Rob Bolton <rab26@aber.ac.uk>
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

from ..database import db, UserAccount

from ..api import api
from ..api.responses import *
from ..api.filters import generate_base_query_filters, get_filters_and_joins

from ..decorators import token_required

from flask import request, current_app, jsonify, send_file
from marshmallow import ValidationError

from datetime import datetime

from ..auth.models import UserAccount
from .models import Donor
from .views import donor_schema, donors_schema, new_donor_schema


@api.route("/donor")
@token_required
def donor_home(tokenuser: UserAccount):
    filters, allowed = generate_base_query_filters(tokenuser, "view")

    if not allowed:
        return not_allowed()

    print(Donor.query.all())
    return success_with_content_response(
        donors_schema.dump(Donor.query.all())
    )

@api.route("/donor/LIMBDON-<id>")
@token_required
def donor_view(id, tokenuser: UserAccount):
    return success_with_content_response(
        donor_schema.dump(
            Donor.query.filter_by(id=id).first()
        )
    )

@api.route("/donor/LIMBDON-<id>/edit", methods=["PUT"])
@token_required
def donor_edit(id, tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        result = new_donor_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    donor = Donor.query.filter_by(id=id).first()

    for attr, value in values.items():
        setattr(donor, attr, value)

    donor.editor_id = tokenuser.id

    try:
        db.session.add(donor)
        db.session.commit()
        db.session.flush()
        return success_with_content_response(
            donor_schema.dump(donor)
        )
    except Exception as err:
        return transaction_error_response(err)

@api.route("/donor/new", methods=["POST"])
@token_required
def donor_new(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        result = new_donor_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    new_donor = Donor(**result)
    new_donor.author_id = tokenuser.id
    print('good', new_donor.id)

    try:
        db.session.add(new_donor)
        db.session.commit()
        db.session.flush()
        return success_with_content_response(
            donor_schema.dump(new_donor)
        )
    except Exception as err:
        return transaction_error_response(err)