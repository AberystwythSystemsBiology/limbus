# Copyright (C) 2021 Keiron O'Shea <keo7@aber.ac.uk>
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
from ..api import api, db
from ..api.responses import *
from ..api.filters import generate_base_query_filters, get_filters_and_joins
from ..api.generics import generic_edit

from ..decorators import token_required
from ..misc import get_internal_api_header

from flask import request, current_app, url_for
from marshmallow import ValidationError
from sqlalchemy.sql import func

from .views import (
    containers_schema,
    container_schema,
    general_container_schema,
    general_containers_schema,
    new_general_container_schema,
    new_container_schema,
    new_container_fixation_type_schema,
    container_fixation_type_schema,
    container_fixation_types_schema,
    ContainerSchema

)

from ..webarg_parser import use_args, use_kwargs, parser

from ..database import (
    UserAccount,
    Container,
    GeneralContainer,
    ContainerFixationType
)


@api.route("/container", methods=["GET"])
@token_required
def container_index(tokenuser: UserAccount):
    return success_with_content_response(
        containers_schema.dump(
            Container.query.all()
        )
    )


@api.route("/container/query", methods=["GET"])
@use_args(ContainerSchema(), location="json")
@token_required
def container_query(args, tokenuser: UserAccount):
    filters, joins = get_filters_and_joins(args, Container)
    return success_with_content_response(
        containers_schema.dump(
            Container.query.filter_by(**filters).filter(*joins).all()
        )
    )

@api.route("/fixation", methods=["GET"])
@token_required
def container_fixation_index(tokenuser: UserAccount):
    return success_with_content_response(
        container_fixation_types_schema.dump(
            ContainerFixationType.query.all()
        )
    )

@api.route("/container/view/container/LIMBCT-<id>", methods=["GET"])
@token_required
def container_view_container(id, tokenuser: UserAccount):
    return success_with_content_response(container_schema.dump(
        Container.query.filter_by(id=id).first_or_404()
    ))


@api.route("/container/view/fixation/LIMBFIX-<id>", methods=["GET"])
@token_required
def container_view_fixation(id, tokenuser: UserAccount):
    return success_with_content_response(container_fixation_type_schema.dump(
        ContainerFixationType.query.filter_by(id=id).first_or_404()
    ))



@api.route("/container/edit/container/LIMBCT-<id>", methods=["PUT"])
@token_required
def container_edit_container(id, tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        container_result = new_container_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    general_container = values["container"]

    general_container_edit_response = requests.put(
        url_for("api.container_edit_general_container", id=id, _external=True),
        headers=get_internal_api_header(tokenuser),
        json=general_container
    )

    if general_container_edit_response.status_code == 200:

        del values["container"]

        existing = Container.query.get(id)

        if not existing:
            return not_found()

        existing.update(values)
        existing.editor_id = tokenuser.id

        try:
            db.session.commit()
            db.session.flush()

            return success_with_content_response(
                container_schema.dump(existing)
            )
        except Exception as err:
            return transaction_error_response(err)

    else:
        return (
            general_container_edit_response.text,
            general_container_edit_response.status_code,
            general_container_edit_response.headers.items(),
        )

@api.route("/container/edit/fixationtype/LIMBFIX-<id>", methods=["PUT"])
@token_required
def container_edit_fixation(id, tokenuser: UserAccount):
    values = request.get_json()
    record = ContainerFixationType.query.get(id)

    if not values:
        return no_values_response()

    try:
        container_result = new_container_fixation_type_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    general_container = values["container"]

    general_container_edit_response = requests.put(
        url_for("api.container_edit_general_container", id=record.container.id, _external=True),
        headers=get_internal_api_header(tokenuser),
        json=general_container
    )

    if general_container_edit_response.status_code == 200:

        del values["container"]

        existing = ContainerFixationType.query.get(id)

        if not existing:
            return not_found()

        existing.update(values)
        existing.editor_id = tokenuser.id

        try:
            db.session.commit()
            db.session.flush()

            return success_with_content_response(
                container_fixation_type_schema.dump(existing)
            )
        except Exception as err:
            return transaction_error_response(err)

    else:
        return (
            general_container_edit_response.text,
            general_container_edit_response.status_code,
            general_container_edit_response.headers.items(),
        )


@api.route("/container/edit/general_container/<id>", methods=["PUT"])
@token_required
def container_edit_general_container(id, tokenuser: UserAccount):
    values = request.get_json()

    return generic_edit(
        db, GeneralContainer, id, new_general_container_schema, general_container_schema, values, tokenuser
    )

@api.route("/container/new/fixationtype/", methods=["POST"])
@token_required
def new_fixation_type(tokenuser: UserAccount):

    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        fixation_type = new_container_fixation_type_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    # Container

    g_container_response = requests.post(
        url_for(
            "api.new_general_container",
            _external=True
        ),
        headers=get_internal_api_header(tokenuser),
        json=values["container"],
    )

    if g_container_response.status_code == 200:
        general_container_info = g_container_response.json()["content"]
    else:
        return (
            g_container_response.text,
            g_container_response.status_code,
            g_container_response.headers.items(),
        )

    new_fixation_type = ContainerFixationType(
        formulation=values["formulation"],
        start_hour=values["start_hour"],
        end_hour=values["start_hour"],
        general_container_id=general_container_info["id"],
        author_id=tokenuser.id
    )

    try:
        db.session.add(new_fixation_type)
        db.session.commit()
        db.session.flush()

        return success_with_content_response(
            container_fixation_type_schema.dump(new_fixation_type)
        )
    except Exception as err:
        return transaction_error_response(err)


@api.route("/container/new/container", methods=["POST"])
@token_required
def new_container(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        container_result = new_container_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)


    g_container_response = requests.post(
        url_for(
            "api.new_general_container",
            _external=True
        ),
        headers=get_internal_api_header(tokenuser),
        json=values["container"],
    )

    if g_container_response.status_code == 200:
        general_container_info = g_container_response.json()["content"]

    else:
        return (
            g_container_response.text,
            g_container_response.status_code,
            g_container_response.headers.items(),
        )

    new_container = Container(
        cellular=values["cellular"],
        fluid=values["fluid"],
        tissue=values["tissue"],
        sample_rack=values["sample_rack"],
        general_container_id=general_container_info["id"],
        author_id=tokenuser.id
    )

    try:
        db.session.add(new_container)
        db.session.commit()
        db.session.flush()

        return success_with_content_response(
            container_schema.dump(new_container)
        )
    except Exception as err:
        return transaction_error_response(err)


@api.route("/container/new/general", methods=["POST"])
@token_required
def new_general_container(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        general_container_result = new_general_container_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    general_container = GeneralContainer(**general_container_result)
    general_container.author_id = tokenuser.id

    try:
        db.session.add(general_container)
        db.session.commit()
        db.session.flush()

        return success_with_content_response(
            general_container_schema.dump(general_container)
        )
    except Exception as err:
        return transaction_error_response(err)

@api.route("/container/lock/container/LIMBCT-<id>", methods=["GET","POST"])
@token_required
def container_lock_container(id, tokenuser: UserAccount):
    existing = Container.query.get(id)
    if existing is None:
        no_values_response()
    existing.is_locked = not existing.is_locked

    try:
        db.session.commit()
        db.session.flush()
        return success_with_content_response(existing.is_locked)
    except Exception as err:
        return transaction_error_response(err)

@api.route("/container/lock/fixationtype/LIMBFIX-<id>", methods=["GET","POST"])
@token_required
def container_lock_fixation(id, tokenuser: UserAccount):
    existing = ContainerFixationType.query.get(id)
    if existing is None:
        no_values_response()
    existing.is_locked = not existing.is_locked

    try:
        db.session.commit()
        db.session.flush()
        return success_with_content_response(existing.is_locked)
    except Exception as err:
        return transaction_error_response(err)


