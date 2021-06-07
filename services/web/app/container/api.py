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

from ..api import api, db
from ..api.responses import *
from ..api.filters import generate_base_query_filters, get_filters_and_joins
from ..decorators import token_required

from flask import request, current_app, url_for
from marshmallow import ValidationError
from sqlalchemy.sql import func

from .views import (
    containers_schema,
    container_schema
)

from ..webarg_parser import use_args, use_kwargs, parser

from ..database import (
    UserAccount,
    Container,
    GeneralContainer
)


@api.route("/container", methods=["GET"])
@token_required
def container_home(tokenuser: UserAccount):
    containers = Container.query.all()
    return success_with_content_response(containers_schema.dumps(containers))

@api.route("/container/new/container", methods=["POST"])
@token_required
def new_container(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()


@api.route("/container/new/general", methods=["POST"])
@token_required
def new_general_container(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        general_container_result = new_general_container(values)
    except ValidationError as err:
        return validation_error_response(err)

    general_container = GeneralContainer(**general_container_result)
    general_container.author_id = tokenuser.id

    try:
        db.session.add(general_container)
        db.session.commit()
        db.session.flush()

        return success_with_content_response(
            container_schema.dump(general_container)
        )
    except Exception as err:
        return transaction_error_response(err)


