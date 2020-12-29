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

import os
from ..api import api
from ..api.responses import *
from ..api.filters import generate_base_query_filters, get_filters_and_joins
import io

from ..database import db

from flask import request, current_app, jsonify, send_file
from ..decorators import token_required

from marshmallow import ValidationError

from .views import (
    document_schema,
    documents_schema,
    document_file_schema,
    basic_document_schema,
    basic_documents_schema,
    new_document_schema,
    new_document_file_schema,
    DocumentSearchSchema,
)


from ..database import UserAccount, Document, DocumentFile
from .encryption import encrypt_document, decrypt_document
from ..webarg_parser import use_args, use_kwargs, parser


@api.route("/document")
@token_required
def document_home(tokenuser: UserAccount):
    filters, allowed = generate_base_query_filters(tokenuser, "view")

    if not allowed:
        return not_allowed()

    return success_with_content_response(
        basic_documents_schema.dump(Document.query.filter_by(**filters).all())
    )


@api.route("/document/LIMBDOC-<id>")
@token_required
def document_view_document(id: int, tokenuser: UserAccount):
    return success_with_content_response(
        document_schema.dump(Document.query.filter_by(id=id).first())
    )


@api.route("/document/query", methods=["GET"])
@use_args(DocumentSearchSchema(), location="json")
@token_required
def document_query(args, tokenuser: UserAccount):
    filters, joins = get_filters_and_joins(args, Document)

    return success_with_content_response(
        basic_documents_schema.dump(
            Document.query.filter_by(**filters).filter(*joins).all()
        )
    )


@api.route("/document/LIMBDOC-<id>/lock", methods=["PUT"])
@token_required
def document_lock_document(id: int, tokenuser: UserAccount):
    document = Document.query.filter_by(id=id).first()

    if not document:
        return not_found()

    document.is_locked = not document.is_locked
    document.editor_id = tokenuser.id

    db.session.add(document)
    db.session.commit()
    db.session.flush()

    return success_with_content_response(basic_document_schema.dump(document))


@api.route("/document/LIMBDOC-<id>/edit", methods=["PUT"])
@token_required
def document_edit_document(id: int, tokenuser: UserAccount):
    document = Document.query.filter_by(id=id).first()

    if not document:
        return not_found()

    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        result = new_document_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    for attr, value in values.items():
        setattr(document, attr, value)

    document.editor_id = tokenuser.id

    try:
        db.session.add(document)
        db.session.commit()
        db.session.flush()

        return success_with_content_response(basic_document_schema.dump(document))
    except Exception as err:
        return transaction_error_response(err)


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
    new_document.author_id = tokenuser.id

    try:
        db.session.add(new_document)
        db.session.commit()
        db.session.flush()
        return success_with_content_response(basic_document_schema.dump(new_document))
    except Exception as err:
        return transaction_error_response(err)


@api.route("/document/LIMBDOC-<id>/file/new", methods=["POST"])
@token_required
def document_upload_file(id, tokenuser: UserAccount):
    def _generate_filepath(name) -> str:
        return os.path.join(current_app.config["DOCUMENT_DIRECTORY"], name)

    def _write_to_file(b_obj: bytes, path: str) -> None:
        with open(path, "wb") as outfile:
            outfile.write(b_obj)
        outfile.close()

    filename = request.args.get("filename")

    if not filename:
        return no_values_response()

    checksum, encrypted_file = encrypt_document(request.data)

    values = {
        "name": filename,
        "checksum": checksum,
        "document_id": id,
        "path": _generate_filepath(filename),
    }

    try:
        result = new_document_file_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    try:
        new_file = DocumentFile(**result)
        new_file.author_id = tokenuser.id
        _write_to_file(encrypted_file, values["path"])
        db.session.add(new_file)
        db.session.commit()
        db.session.flush()
        return success_with_content_response(document_file_schema.dump(new_file))
    except Exception as err:
        return transaction_error_response(err)


@api.route("/document/LIMBDOC-<id>/<file_id>/lock", methods=["POST"])
@token_required
def document_file_lock(id, file_id, tokenuser: UserAccount):
    file = DocumentFile.query.filter_by(id=file_id, document_id=id).first()

    if not file:
        return {"success": False, "messages": "There's an issue here"}, 417

    file.is_locked = not file.is_locked
    file.editor_id = tokenuser.id
    db.session.add(file)
    db.session.commit()
    db.session.flush()

    return success_with_content_response(document_file_schema.dump(file))


@api.route("/document/LIMBDOC-<id>/<file_id>", methods=["GET"])
@token_required
def document_file_get(id, file_id):
    file = DocumentFile.query.filter_by(id=file_id, document_id=id).first()

    if not file:
        return {"success": False, "messages": "There's an issue here"}, 417

    f = open(file.path, "rb").read()
    document = decrypt_document(f, file.checksum)
    return (
        send_file(
            io.BytesIO(document), as_attachment=True, attachment_filename=file.name
        ),
        200,
    )
