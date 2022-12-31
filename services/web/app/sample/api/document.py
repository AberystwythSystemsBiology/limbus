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

from flask import request, url_for
from marshmallow import ValidationError
from ...api import api, generics
from ...api.responses import *
from ...decorators import token_required, requires_roles
from ...misc import get_internal_api_header

from ..views import new_document_to_sample_schema, sample_document_schema

from ...database import (
    db,
    SampleDocument,
    SampleConsent,
    SampleConsentAnswer,
    UserAccount,
)


@api.route("/sample/associate/document", methods=["POST"])
#@token_required
@requires_roles("data_entry")
def sample_to_document(tokenuser: UserAccount):
    values = request.get_json()
    return generics.generic_new(
        db,
        SampleDocument,
        new_document_to_sample_schema,
        sample_document_schema,
        values,
        tokenuser,
    )
