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
    edit_donor_schema,
    DonorSearchSchema,
    new_donor_diagnosis_event_schema,
    donor_diagnosis_event_schema,
)

from ..sample.models import SampleConsent, SampleConsentAnswer, Sample
from ..sample.views import new_consent_schema, new_consent_answer_schema, consent_schema


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


@api.route("/donor/LIMBDON-<id>/view")
@token_required
def donor_edit_view(id, tokenuser: UserAccount):
    return success_with_content_response(
        new_donor_schema.dump(Donor.query.filter_by(id=id).first())
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



@api.route("/donor/new/consent", methods=["POST"])
@token_required
def donor_new_consent(tokenuser: UserAccount):
    values = request.get_json()
    if not values:
        return no_values_response()

    errors = {}
    for key in ["identifier", "donor_id", "comments", "template_id", "date", "answers"]:
        if key not in values.keys():
            errors[key] = ["Not found."]

    if len(errors.keys()) > 0:
        return validation_error_response(errors)

    answers = values["answers"]
    values.pop("answers")

    try:
        consent_result = new_consent_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    new_consent = SampleConsent(**consent_result)
    new_consent.author_id = tokenuser.id

    try:
        db.session.add(new_consent)
        db.session.flush()
        db.session.commit()
    except Exception as err:
        return transation_error_response(err)

    for answer in answers:
        try:
            answer_result = new_consent_answer_schema.load(
                {"question_id": int(answer), "consent_id": new_consent.id}
            )
        except ValidationError as err:
            return validation_error_response(err)

        new_answer = SampleConsentAnswer(**answer_result)
        new_answer.author_id = tokenuser.id
        db.session.add(new_answer)

    try:
        db.session.commit()
    except Exception as err:
        # Delete the new consent from database to avoid duplicates
        db.session.delete(new_consent)
        db.session.commit()
        return transaction_error_response(err)

    return success_with_content_response(
        consent_schema.dump(SampleConsent.query.filter_by(id=new_consent.id).first())
    )

@api.route("/donor/consent/<id>/remove", methods=["POST"])
@token_required
def donor_remove_consent(id, tokenuser: UserAccount):
    consent = SampleConsent.query.filter_by(id=id).first()
    if consent:
        if consent.is_locked:
            return locked_response("donor consent! ")
    else:
        return not_found("donor consent(%s)" % id)

    donor_id = None
    if consent.donor_id is not None:
        donor = Donor.query.filter_by(id=consent.donor_id). \
            with_entities(Donor.uuid, Donor.is_locked).first()
        donor_id = consent.donor_id

        if donor:
            if donor.is_locked:
                return locked_response("donor LIMBDON-(%s)" % donor.id)
        else:
            return not_found("related donor")

    samples = Sample.query.filter_by(consent_id=id).all()
    ns = len(samples)
    if ns > 0:
        return in_use_response("%d sample(s)" % ns)

    msg = "";
    answers = SampleConsentAnswer.query.filter_by(consent_id=id).all()
    if answers:
        try:
            for answer in answers:
                db.session.delete(answer)
            db.session.commit()
            msg = "Consent answers deleted!"
        except Exception as err:
            return transaction_error_response(err)

    try:
        db.session.delete(consent)
        db.session.commit()
        return success_with_content_response(donor_id)
    except Exception as err:
        return transaction_error_response(msg +" | " + err)
