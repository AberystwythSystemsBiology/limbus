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

from ..webarg_parser import use_args

from ..api import api, get_filters_and_joins
from ..api.responses import *

from marshmallow import ValidationError

from flask import request
from ..decorators import token_required

from .views import (
    new_consent_form_template_schema,
    basic_consent_form_template_schema,
    basic_consent_form_templates_schema,
    new_consent_form_question_schema,
    consent_form_template_schema,
    consent_form_question_schema,
    basic_consent_form_question_schema,
    ConsentFormTemplateSearchSchema,
)

from ..auth.models import UserAccount
from .models import ConsentFormTemplate, ConsentFormTemplateQuestion


@api.route("/consent")
@token_required
def consent_home(tokenuser: UserAccount):
    return success_with_content_response(
        basic_consent_form_templates_schema.dump(ConsentFormTemplate.query.all())
    )


@api.route("/consent/LIMBPCF-<id>")
@token_required
def consent_view_template(id, tokenuser: UserAccount):
    return success_with_content_response(
        consent_form_template_schema.dump(
            ConsentFormTemplate.query.filter_by(id=id).first()
        )
    )


@api.route("/consent/query", methods=["GET"])
@use_args(ConsentFormTemplateSearchSchema(), location="json")
@token_required
def consent_query(args, tokenuser: UserAccount):
    print(args)
    filters, joins = get_filters_and_joins(args, ConsentFormTemplate)

    return success_with_content_response(
        basic_consent_form_templates_schema.dump(
            ConsentFormTemplate.query.filter_by(**filters).filter(*joins).all()
        )
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
            basic_consent_form_template_schema.dump(new_template)
        )
    except Exception as err:
        return transaction_error_response(err)


@api.route("/content/LIMBPCF-<id>/edit", methods=["PUT"])
@token_required
def consent_edit_template(id, tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        result = new_consent_form_template_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    template = ConsentFormTemplate.query.filter_by(id=id).first()

    for attr, value in values.items():
        setattr(template, attr, value)

    template.editor_id = tokenuser.id

    try:
        db.session.add(template)
        db.session.commit()
        db.session.flush()
        return success_with_content_response(
            basic_consent_form_template_schema.dump(template)
        )
    except Exception as err:
        return transaction_error_response(err)


@api.route("/consent/LIMBPCF-<id>/lock", methods=["PUT"])
@token_required
def consent_lock_template(id: int, tokenuser: UserAccount):
    template = ConsentFormTemplate.query.filter_by(id=id).first()

    if not template:
        return not_found()

    template.is_locked = not template.is_locked
    template.editor_id = tokenuser.id

    db.session.add(template)
    db.session.commit()
    db.session.flush()

    return success_with_content_response(
        basic_consent_form_template_schema.dump(template)
    )


@api.route("/consent/LIMBPCF-<id>/question/new", methods=["POST"])
@token_required
def consent_add_question(id, tokenuser: UserAccount):
    template = ConsentFormTemplate.query.filter_by(id=id).first()
    values = request.get_json()

    if not template:
        return not_found()

    if not values:
        return no_values_response()

    try:
        result = new_consent_form_question_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    new_question = ConsentFormTemplateQuestion(**result)
    new_question.author_id = tokenuser.id
    new_question.template_id = id

    try:
        db.session.add(new_question)
        db.session.commit()
        db.session.flush()
        return success_with_content_response(
            basic_consent_form_question_schema.dump(new_question)
        )
    except Exception as err:
        return validation_error_response(err)


@api.route("/consent/LIMBPCF-<id>/question/<q_id>/edit", methods=["PUT"])
@token_required
def consent_edit_question(id, q_id, tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        result = new_consent_form_question_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    question = ConsentFormTemplateQuestion.query.filter_by(
        id=q_id, template_id=id
    ).first()

    for attr, value in values.items():
        setattr(question, attr, value)

    question.editor_id = tokenuser.id

    try:
        db.session.add(question)
        db.session.commit()
        db.session.flush()
        return success_with_content_response(
            basic_consent_form_question_schema.dump(question)
        )
    except Exception as err:
        return transaction_error_response(err)


@api.route("/consent/LIMBPCF-<id>/question/<q_id>")
@token_required
def consent_view_question(id, q_id, tokenuser: UserAccount):
    return success_with_content_response(
        consent_form_question_schema.dump(
            ConsentFormTemplateQuestion.query.filter_by(id=q_id, template_id=id).first()
        )
    )
