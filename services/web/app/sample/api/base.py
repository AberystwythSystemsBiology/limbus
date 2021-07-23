# Copyright (C) 2020  Keiron O'Shea <keo7@aber.ac.uk>
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

from flask import request, abort, url_for
from marshmallow import ValidationError
from ...api import api, generics
from ...api.responses import *
from ...api.filters import generate_base_query_filters, get_filters_and_joins

from ...decorators import token_required
from ...misc import get_internal_api_header
from ...webarg_parser import use_args, use_kwargs, parser

from ..views import (
    basic_samples_schema,
    basic_sample_schema,
    sample_protocol_event_schema,
    sample_schema,
    SampleFilterSchema,
    new_fluid_sample_schema,
    sample_type_schema,
    new_cell_sample_schema,
    new_molecular_sample_schema,
    new_sample_schema,
)

from ...database import db, Sample, SampleToType, UserAccount

from ..enums import *

import requests


@api.route("/sample/containers", methods=["GET"])
def sample_get_containers():
    return success_with_content_response(
        {
            "Fluid": {"container": FluidContainer.choices()},
            "Molecular": {"container": FluidContainer.choices()},
            "Cell": {
                "container": CellContainer.choices(),
                "fixation_type": FixationType.choices(),
            },
        }
    )


@api.route("/sample", methods=["GET"])
@token_required
def sample_home(tokenuser: UserAccount):
    return success_with_content_response(basic_samples_schema.dump(Sample.query.all()))


@api.route("/sample/query", methods=["GET"])
@use_args(SampleFilterSchema(), location="json")
@token_required
def sample_query(args, tokenuser: UserAccount):
    filters, joins = get_filters_and_joins(args, Sample)
    print("filters: ", filters)
    print("joins: ", joins)
    return success_with_content_response(
        basic_samples_schema.dump(
            Sample.query.filter_by(**filters).filter(*joins).all()
        )
    )


@api.route("/sample/<uuid>", methods=["GET"])
@token_required
def sample_view_sample(uuid: str, tokenuser: UserAccount):
    sample = Sample.query.filter_by(uuid=uuid).first()

    if sample:
        return success_with_content_response(sample_schema.dump(sample))
    else:
        return not_found()


@api.route("sample/new", methods=["POST"])
@token_required
def sample_new_sample(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    errors = {}
    for key in [
        "collection_information",
        "sample_information",
        "sample_type_information",
        "consent_information"
    ]:
        if key not in values.keys():
            errors[key] = ["Not found."]

    if len(errors.keys()) > 0:
        return validation_error_response(errors)

    sample_type_response = requests.post(
        url_for(
            "api.sample_new_sample_type",
            base_type=values["sample_information"]["base_type"],
            _external=True,
        ),
        headers=get_internal_api_header(tokenuser),
        json=values["sample_type_information"],
    )

    if sample_type_response.status_code == 200:
        sample_type_information = sample_type_response.json()["content"]

    else:
        return (
            sample_type_response.text,
            sample_type_response.status_code,
            sample_type_response.headers.items(),
        )

    consent_response = requests.post(
        url_for("api.sample_new_sample_consent", _external=True),
        headers=get_internal_api_header(tokenuser),
        json=values["consent_information"],
    )

    if consent_response.status_code == 200:
        consent_information = consent_response.json()["content"]
    else:
        return (
            consent_response.text,
            consent_response.status_code,
            consent_response.headers.items(),
        )

    sample_information = values["sample_information"]
    sample_information["consent_id"] = consent_information["id"]
    sample_information["sample_to_type_id"] = sample_type_information["id"]

    try:
        sample_values = new_sample_schema.load(sample_information)
    except ValidationError as err:
        return validation_error_response(err)

    new_sample = Sample(**sample_values)
    new_sample.author_id = tokenuser.id
    new_sample.remaining_quantity = sample_values["quantity"]

    try:
        db.session.add(new_sample)
        db.session.commit()
        db.session.flush()
    except Exception as err:
        return transaction_error_response(err)

    values["collection_information"]["sample_id"] = new_sample.id

    protocol_event_response = requests.post(
        url_for("api.sample_new_sample_protocol_event", _external=True),
        headers=get_internal_api_header(tokenuser),
        json=values["collection_information"],
    )

    if protocol_event_response.status_code == 200:
        collection_event = protocol_event_response.json()["content"]
    else:
        return (
            protocol_event_response.text,
            protocol_event_response.status_code,
            protocol_event_response.headers.items(),
        )

    if "container_information" in values:
        pass

    return success_with_content_response(
        basic_sample_schema.dump(
            Sample.query.filter_by(id=new_sample.id).first_or_404()
        )
    )


@api.route("sample/new/sample_type_instance/<base_type>", methods=["POST"])
@token_required
def sample_new_sample_type(base_type: str, tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    if base_type == "FLU":
        schema = new_fluid_sample_schema
    elif base_type == "CEL":
        schema = new_cell_sample_schema
    elif base_type == "MOL":
        schema = new_molecular_sample_schema
    else:
        return validation_error_response({"base_type": ["Not a valid base_type."]})

    try:
        new_schema = schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    sampletotype = SampleToType(**new_schema)
    sampletotype.author_id = tokenuser.id

    db.session.add(sampletotype)

    try:
        db.session.commit()
        db.session.flush()
        return success_with_content_response(sample_type_schema.dump(sampletotype))
    except Exception as err:
        return transaction_error_response(err)
