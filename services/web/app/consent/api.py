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

from .. import db

from ..api import api
from ..api.responses import *

from marshmallow import ValidationError

from flask import request
from ..decorators import token_required

from .views import (
    new_consent_form_template_schema,
    basic_consent_form_templates_schema,
    new_consent_form_templates_schema,
)

from ..auth.models import UserAccount
from .models import ConsentFormTemplate

@api.route("/consent")
@token_required
def consent_home(tokenuser: UserAccount):
    return success_with_content_response(
        basic_consent_form_templates_schema.dump(ConsentFormTemplate.query.all())
    )

@api.route("/consent/new_template", methods=["POST"])
@token_required
def consent_new_template(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        result = new_consent_form_template_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    new_template = ConsentFormTemplate(**result)
    new_template.author_id = tokenuser.id

    try:
        db.session.add(new_template)
        db.session.commit()
        db.session.flush()
        return success_with_content_response(
            basic_consent_form_templates_schema.dump(new_template)
        )
    except Exception as err:
        return transaction_error_response(err)