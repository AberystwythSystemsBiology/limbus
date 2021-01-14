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

from ..database import db, UserAccount, DonorDiagnosisEvent, Donor, DonorToSample

from ..api import api
from ..api.responses import *
from ..api.filters import generate_base_query_filters, get_filters_and_joins

from ..decorators import token_required

from flask import request, current_app, jsonify, send_file
from marshmallow import ValidationError

from sqlalchemy.sql import func
from ..webarg_parser import use_args, use_kwargs, parser


from ..auth.models import UserAccount

from .views import (
    donor_schema,
    donors_schema,
    new_donor_schema,
    DonorSearchSchema,
    new_donor_diagnosis_event_schema,
    donor_diagnosis_event_schema,
)


@api.route("/donor")
@token_required
def donor_home(tokenuser: UserAccount):
    filters, allowed = generate_base_query_filters(tokenuser, "view")

    if not allowed:
        return not_allowed()

    return success_with_content_response(donors_schema.dump(Donor.query.all()))


@api.route("/donor/query", methods=["GET"])
@use_args(DonorSearchSchema(), location="json")
@token_required
def donor_query(args, tokenuser: UserAccount):
    filters, joins = get_filters_and_joins(args, Donor)
    return success_with_content_response(
        donors_schema.dump(Donor.query.filter_by(**filters).filter(*joins).all())
    )


@api.route("/donor/LIMBDON-<id>")
@token_required
def donor_view(id, tokenuser: UserAccount):
    return success_with_content_response(
        donor_schema.dump(Donor.query.filter_by(id=id).first())
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
    donor.updated_on = func.now()

    try:
        db.session.add(donor)
        db.session.commit()
        db.session.flush()
        return success_with_content_response(donor_schema.dump(donor))
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

    try:
        db.session.add(new_donor)
        db.session.commit()
        db.session.flush()
        return success_with_content_response(donor_schema.dump(new_donor))
    except Exception as err:
        return transaction_error_response(err)


@api.route("/donor/LIMBDON-<id>/associate/sample", methods=["POST"])
@token_required
def donor_associate_sample(id, tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    new_diagnosis_to_sample = DonorToSample(sample_id=values["sample_id"], donor_id=id)

    new_diagnosis_to_sample.author_id = tokenuser.id

    try:
        db.session.add(new_diagnosis_to_sample)
        db.session.commit()
        db.session.flush()
        return success_with_content_response(
            {"sample_id": values["sample_id"], "donor_id": id}
        )
    except Exception as err:
        return transaction_error_response(err)


@api.route("/donor/LIMBDON-<id>/associate/diagnosis", methods=["POST"])
@token_required
def donor_new_diagnosis(id, tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        # New view
        values["donor_id"] = id
        result = new_donor_diagnosis_event_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    new_diagnosis = DonorDiagnosisEvent(**result)
    new_diagnosis.author_id = tokenuser.id

    try:
        db.session.add(new_diagnosis)
        db.session.commit()
        db.session.flush()
        return success_with_content_response(
            donor_diagnosis_event_schema.dump(new_diagnosis)
        )
    except Exception as err:
        return transaction_error_response(err)
