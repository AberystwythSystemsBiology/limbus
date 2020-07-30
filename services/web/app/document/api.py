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

from ..api import api
from ..api.responses import *

from .. import db
from flask import request, current_app, jsonify
from ..decorators import token_required

from marshmallow import ValidationError

from .views import (
    document_schema,
    documents_schema,
    basic_documents_schema,
    new_document_schema,
)

from ..auth.models import UserAccount
from .models import Document, DocumentFile

@api.route("/document")
@token_required
def document_home(tokenuser: UserAccount):
    return success_with_content_response(
        basic_documents_schema.dump(Document.query.all())
    )

@api.route("/document/new", methods=["POST"])
@token_required
def document_new_document(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()


    try:
        result = new_document_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    new_document = Document(**result)
    new_document.created_by = tokenuser.id

    try:
        db.session.add(new_document)
        db.session.commit()
        db.session.flush()
        return success_with_content_response(
            basic_documents_schema.dump(new_document)
        )
    except Exception as err:
        return transaction_error_response(err)