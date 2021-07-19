# Copyright (C) 2021  Keiron O'Shea <keo7@aber.ac.uk>
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

import requests
from flask import request, abort, url_for, flash
from marshmallow import ValidationError
from ...api import api, generics
from ...api.responses import *
from ...api.filters import generate_base_query_filters, get_filters_and_joins
from ...webarg_parser import use_args, use_kwargs, parser

from ...decorators import token_required
from ...misc import get_internal_api_header
from ...database import (
    db,
    SampleToContainerType,UserAccount
)

from ..views import (
    sample_to_container_schema,
    new_sample_to_container_schema,
    new_sample_to_fixation_schema
)


@api.route("/sample/new/fixation", methods=["POST"])
@token_required
def sample_new_fixation(tokenuser: UserAccount):
    values: dict = request.get_json()

    if not values:
        return no_values_response()

    sample_response = requests.get(
        url_for("api.sample_view_sample", uuid=values["sample_uuid"], _external=True),
        headers=get_internal_api_header(tokenuser),
    )

    if sample_response.status_code == 200:
        try:

            sample = sample_response.json()["content"]

            sample_to_fixation_values = new_sample_to_fixation_schema.load({
                "sample_id": sample["id"],
                "fixation_id": values["container_id"],
                "type": values["type"]
            })

        except ValidationError as err:
            return validation_error_response(err)

        new_sample_to_fixation = SampleToContainerType(**sample_to_fixation_values)
        new_sample_to_fixation.author_id = tokenuser.id

        try:
            db.session.add(new_sample_to_fixation)
            db.session.commit()
            db.session.flush()

            return success_with_content_response(
                sample_to_container_schema.dump(new_sample_to_fixation)
            )

        except Exception as err:
            return transaction_error_response(err)

    else:
        return (
            sample_response.text,
            sample_response.status_code,
            sample_response.headers.items(),
        )


@api.route("/sample/new/container", methods=["POST"])
@token_required
def sample_new_container(tokenuser: UserAccount):
    values: dict = request.get_json()

    if not values:
        return no_values_response()

    sample_response = requests.get(
        url_for("api.sample_view_sample", uuid=values["sample_uuid"], _external=True),
        headers=get_internal_api_header(tokenuser),
    )

    if sample_response.status_code == 200:
        try:

            sample = sample_response.json()["content"]

            sample_to_container_values = new_sample_to_container_schema.load({
                "sample_id": sample["id"],
                "container_id": values["container_id"],
                "type": values["type"]
            })

        except ValidationError as err:
            return validation_error_response(err)

        new_sample_to_container = SampleToContainerType(**sample_to_container_values)
        new_sample_to_container.author_id = tokenuser.id

        try:
            db.session.add(new_sample_to_container)
            db.session.commit()
            db.session.flush()

            return success_with_content_response(
                sample_to_container_schema.dump(new_sample_to_container)
            )

        except Exception as err:
            return transaction_error_response(err)

    else:
        return (
            sample_response.text,
            sample_response.status_code,
            sample_response.headers.items(),
        )
