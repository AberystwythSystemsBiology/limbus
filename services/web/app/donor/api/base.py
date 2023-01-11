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

from ...database import (
    db,
    UserAccount,
    DonorDiagnosisEvent,
    Donor,
    DonorToSample,
    Event,
    SampleConsent,
    SampleConsentAnswer,
    SampleConsentWithdrawal,
    SampleDisposal,
    Sample,
    DonorProtocolEvent,
    TemporaryStore,
)

from ...api import api
from ...api.responses import *
from ...api.filters import generate_base_query_filters, get_filters_and_joins
from ...sample.api import func_validate_settings
from ...disease.api import *
from ...decorators import token_required, requires_roles

from flask import request, current_app, jsonify, send_file
from marshmallow import ValidationError

from sqlalchemy.sql import extract, func
from ...webarg_parser import use_args, use_kwargs, parser


from ...auth.models import UserAccount

from ..views import (
    donor_schema,
    donors_schema,
    new_donor_schema,
    edit_donor_schema,
    basic_donors_schema,
    basic_donor_schema,
    DonorSearchSchema,
    new_donor_diagnosis_event_schema,
    donor_diagnosis_event_schema,
    donor_diagnoses_schema,
    new_donor_protocol_event_schema,
    # donor_protocol_events_info_schema,
    NewDonorProtocolEventSchema,
)

from ...event.views import new_event_schema

from ...sample.models import SampleConsent, SampleConsentAnswer, Sample
from ...sample.views import (
    new_consent_schema,
    new_consent_answer_schema,
    consent_schema,
)

from datetime import date


@api.route("/donor/get_study_reference", methods=["GET"])
@use_args(NewDonorProtocolEventSchema(), location="json")
@token_required
def donor_study_reference(args, tokenuser: UserAccount):
    study_id = args.pop("protocol_id", None)
    reference_id = args.pop("reference_id", None)
    refs = (
        db.session.query(DonorProtocolEvent)
        .filter_by(protocol_id=study_id, reference_id=reference_id)
        .all()
    )
    donor_study_references_schema = NewDonorProtocolEventSchema(many=True)

    return success_with_content_response(donor_study_references_schema.dump(refs))


@api.route("/donor")
@token_required
def donor_home(tokenuser: UserAccount):
    filters, allowed = generate_base_query_filters(tokenuser, "view")

    if not allowed:
        return not_allowed()

    return success_with_content_response(donors_schema.dump(Donor.query.all()))


@api.route("/donor/diagnoses", methods=["GET"])
@token_required
def donor_diagnosis_data(tokenuser: UserAccount):
    dde = DonorDiagnosisEvent.query.distinct(DonorDiagnosisEvent.doid_ref).all()
    diagnosis_info = donor_diagnoses_schema.dump(dde)
    # print("diagnosis_info: ", diagnosis_info)
    diagnosis_choices = []
    for diagd in diagnosis_info:
        diag = diagd["doid_ref"]
        # diag_ref = [k for k in diag["references"]]
        # diag_ref = [diag["name"]] + diag_ref
        # diag_ref = ",".join(diag_ref)
        diag_ref = diag["name"]
        diagnosis_choices.append((diag["iri"], "||".join([diag["label"], diag_ref])))

    # print("diagnosis_choices: ", diagnosis_choices)
    return success_with_content_response(
        {
            "info": diagnosis_info,
            "choices": diagnosis_choices,
        }
    )


@api.route("/donor/query_basic", methods=["GET"])
@use_args(DonorSearchSchema(), location="json")
@token_required
def donor_query_basic(args, tokenuser: UserAccount):
    filters, joins = get_filters_and_joins(args, Donor)
    print("filters ", filters)
    print("joins ", joins)
    return success_with_content_response(
        basic_donors_schema.dump(Donor.query.filter_by(**filters).filter(*joins).all())
    )


@api.route("/donor/query", methods=["GET"])
@use_args(DonorSearchSchema(), location="json")
@token_required
def donor_query(args, tokenuser: UserAccount):
    filters, joins = get_filters_and_joins(args, Donor)
    print("filters", filters)
    print("joins", joins)

    diag_refs = filters.pop("diagnosis", None)
    age_min = filters.pop("age_min", None)
    age_max = filters.pop("age_max", None)
    bmi_min = filters.pop("bmi_min", None)
    bmi_max = filters.pop("bmi_max", None)

    stmt = db.session.query(Donor).filter_by(**filters).filter(*joins)
    # print("stmt0: ", stmt.count())

    if diag_refs:
        diag_refs = diag_refs.split(",")
        # print("diag_refs", diag_refs)
        stmt = (
            stmt.join(DonorDiagnosisEvent)
            .filter(DonorDiagnosisEvent.doid_ref.in_(diag_refs))
            .distinct(Donor.id)
        )

    if age_min:
        age_min = int(age_min)
        stmt = stmt.filter(Donor.age_at_registration >= age_min)

    if age_max:
        age_max = int(age_max)
        stmt = stmt.filter(Donor.age_at_registration < age_max)

    if bmi_min:
        bmi_min = float(bmi_min)
        stmt = stmt.filter(Donor.bmi >= bmi_min)

    if bmi_max:
        bmi_max = float(bmi_max)
        stmt = stmt.filter(Donor.bmi < bmi_max)

    results = basic_donors_schema.dump(stmt.all())
    for i in range(len(results)):
        tmp = TemporaryStore.query.filter_by(uuid=results[i]["uuid"], type='SMPC').first()
        results[i].update({"collection_datetime": ""})
        if tmp:
            results[i].update({"collection_datetime": tmp.data["collection_datetime"]})

    return success_with_content_response(results)


@api.route("/donor/LIMBDON-<id>")
@token_required
def donor_view(id, tokenuser: UserAccount):
    results = donor_schema.dump(Donor.query.filter_by(id=id).first())
    # smpls = results["samples"]
    # for i in range(len(smpls)):
    #     tmp = TemporaryStore.query.filter_by(uuid=smpls[i]["uuid"]).first()
    #     smpls[i].update({"collection_datetime": ""})
    #
    #     if tmp:
    #         try:
    #             smpls[i].update({"collection_datetime": tmp.data["collection_datetime"]})
    #         except:
    #             pass

    return success_with_content_response(
        results
    )


@api.route("/donor/LIMBDON-<id>/view")
@token_required
def donor_edit_view(id, tokenuser: UserAccount):
    return success_with_content_response(
        new_donor_schema.dump(Donor.query.filter_by(id=id).first())
    )


@api.route("/donor/LIMBDON-<id>/edit", methods=["PUT"])
#@token_required
@requires_roles("data_entry")
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
#@token_required
@requires_roles("data_entry")
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
#@token_required
@requires_roles("data_entry")
def donor_associate_sample(id, tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    donor_id = id
    sample_id = int(values["sample_id"])

    dts = DonorToSample.query.filter_by(sample_id=sample_id).first()
    if dts:
        return validation_error_response("The sample has been assigned to a donor!")

    # Modify sample consent
    consent = (
        SampleConsent.query.join(Sample, Sample.consent_id == SampleConsent.id)
        .filter(Sample.id == sample_id)
        .first()
    )
    if not consent:
        return not_found("Sample consent")

    old_donor_id = consent.donor_id
    if consent.donor_id is not None:
        return validation_error_response(
            "The sample's consent has been linked to donor LIMBDON-%d!"
            % consent.donor_id
        )
    consent.donor_id = donor_id
    consent.update({"editor_id": tokenuser.id})
    new_donor_to_sample = DonorToSample(
        sample_id=values["sample_id"], donor_id=id, author_id=tokenuser.id
    )
    try:
        db.session.add(consent)
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        return transaction_error_response(err)

    try:
        db.session.add(new_donor_to_sample)
        db.session.commit()
        return success_with_content_message_response(
            {"sample_id": values["sample_id"], "donor_id": id},
            "Sample associated to donor successfully!",
        )
    except Exception as err:
        # Rollback: also set sample consent old_donor_id
        db.session.rollback()
        consent.donor_id = old_donor_id
        db.add(consent)
        db.session.commit()
    return transaction_error_response(err)


@api.route("/donor/LIMBDON-<id>/associate/diagnosis", methods=["POST"])
#@token_required
@requires_roles("data_entry")
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


@api.route("/donor/LIMBDIAG-<id>/remove", methods=["DELETE", "POST"])
#@token_required
@requires_roles("data_entry")
def donor_remove_diagnosis(id, tokenuser: UserAccount):
    dde = DonorDiagnosisEvent.query.filter_by(id=id).first()
    if not dde:
        return no_values_response("Diagnosis Event")

    donor_id = dde.donor_id
    try:
        db.session.delete(dde)
        db.session.commit()
        msg = "Diagnosis %s deleted succesfully! " % dde.id
    except Exception as err:
        return transaction_error_response(err)

    return success_with_content_message_response({"donor_id": donor_id}, msg)


def func_update_donor_protocol_event(
    values, tokenuser: UserAccount, new_protocol_event=None
):
    # values = request.get_json()

    if not values:
        return no_values_response()

    try:
        event_result = new_donor_protocol_event_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    if new_protocol_event:
        # -- update
        new_event = Event.query.filter_by(id=new_protocol_event.event_id).first()
        new_event.update(event_result["event"])
        new_event.update({"editor_id": tokenuser.id})
    else:
        # -- insert new protocol event
        new_event = Event(**event_result["event"])
        new_event.author_id = tokenuser.id

    try:
        db.session.add(new_event)
        db.session.flush()
    except Exception as err:
        return transaction_error_response(err)

    event_result.pop("event")

    if new_protocol_event:
        new_protocol_event.update(event_result)
        new_protocol_event.update({"editor_id": tokenuser.id})
        new_protocol_event.event_id = new_event.id
    else:
        new_protocol_event = DonorProtocolEvent(**event_result)
        new_protocol_event.author_id = tokenuser.id
        new_protocol_event.event_id = new_event.id

    try:
        db.session.add(new_protocol_event)
        db.session.flush()
    except Exception as err:
        return transaction_error_response(err)

    return {"success": True, "new_protocol_event": new_protocol_event}


@api.route("/donor/new/consent", methods=["POST"])
#@token_required
@requires_roles("data_entry")
def donor_new_consent(tokenuser: UserAccount):
    values = request.get_json()
    if not values:
        return no_values_response()

    errors = {}
    for key in [
        "identifier",
        "comments",
        "template_id",
        "date",
        "undertaken_by",
        "answers",
    ]:
        if key not in values.keys():
            errors[key] = ["Not found."]

    if len(errors.keys()) > 0:
        return validation_error_response(errors)

    answers = values.pop("answers")

    study_protocol_id = values.pop("study_protocol_id", None)
    study_event = None
    study = values.pop("study", {})
    if study_protocol_id:
        study["protocol_id"] = study_protocol_id
        if "donor_id" in values:
            study["donor_id"] = values["donor_id"]
        else:
            study.pop("donor_id", None)

        # -- Add donor protocol event
        study_event = func_update_donor_protocol_event(study, tokenuser)
        if not study_event["success"]:
            return study_event

        study_event = study_event["new_protocol_event"]

    try:
        consent_result = new_consent_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    new_consent = SampleConsent(**consent_result)
    new_consent.author_id = tokenuser.id
    new_consent.id = None
    if study_event:
        new_consent.study_event_id = study_event.id

    try:
        # ids = [val for val, in db.session.execute("select nextval('sampleconsent_id_seq')")]
        # nextid=ids[0]
        # new_consent.id = nextid
        db.session.add(new_consent)
        db.session.flush()

    except Exception as err:
        return transaction_error_response(err)

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

        db.session.rollback()
        return transaction_error_response(err)

    consent_info = consent_schema.dump(
        SampleConsent.query.filter_by(id=new_consent.id).first()
    )
    return success_with_content_response(consent_info)


@api.route("/donor/consent/LIMBDC-<id>/edit", methods=["POST"])
#@token_required
@requires_roles("data_entry")
def donor_edit_consent(id, tokenuser: UserAccount):

    new_consent = SampleConsent.query.filter_by(id=id).first()

    if not new_consent:
        return not_found("Consent (LIMBDC-%s)" % id)

    values = request.get_json()
    if not values:
        return no_values_response()

    values.pop("id", 0)

    errors = {}
    for key in [
        "identifier",
        "donor_id",
        "comments",
        "template_id",
        "date",
        "undertaken_by",
        "answers",
    ]:
        if key not in values.keys():
            errors[key] = ["Not found."]

    if len(errors.keys()) > 0:
        return validation_error_response(errors)

    answers = values.pop("answers", [])

    study_event = DonorProtocolEvent.query.filter_by(
        id=new_consent.study_event_id
    ).first()

    study_protocol_id = values.pop("study_protocol_id", None)
    study = values.pop("study", {})

    if study_protocol_id:
        study["protocol_id"] = study_protocol_id
        if "donor_id" in values:
            study["donor_id"] = values["donor_id"]
        else:
            study["donor_id"] = None

        # -- Add/update donor protocol event
        study_event = func_update_donor_protocol_event(study, tokenuser, study_event)
        print("study_event", study_event)
        if not study_event["success"]:
            return study_event

        study_event = study_event["new_protocol_event"]

    try:
        consent_result = new_consent_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    new_consent.update(consent_result)
    new_consent.update({"editor_id": tokenuser.id})

    del_study = False
    if study_protocol_id and study_event:
        new_consent.study_event_id = study_event.id
    elif new_consent.study_event_id:
        new_consent.study_event_id = None
        del_study = True
    else:
        new_consent.study_event_id = None

    try:
        db.session.add(new_consent)
        db.session.flush()
        if del_study:
            db.session.delete(study_event)
    except Exception as err:
        return transaction_error_response(err)

    ans = (
        db.session.query(SampleConsentAnswer.question_id)
        .filter_by(consent_id=new_consent.id)
        .all()
    )
    ans = [q[0] for q in ans]  # -- Get the list of question ids
    print("ans", ans)
    print("answers", answers)
    # -- Delete the ones unchecked
    todel = [q for q in ans if q not in answers]
    for answer in todel:
        ans1 = SampleConsentAnswer.query.filter_by(
            consent_id=new_consent.id, question_id=int(answer)
        ).first()
        if ans1:
            db.session.delete(ans1)

    # -- Add the new checked question
    toadd = [q for q in answers if q not in ans]
    for answer in toadd:
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
        db.session.rollback()
        return transaction_error_response(err)

    consent_info = consent_schema.dump(new_consent)
    return success_with_content_response(consent_info)


@api.route("/donor/consent/withdraw", methods=["POST"])
#@token_required
@requires_roles("data_entry")
def donor_withdraw_consent(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    consent_id = values["consent_id"]
    consent = SampleConsent.query.filter_by(id=consent_id).first()
    if consent:
        if consent.is_locked:
            return locked_response("donor consent! ")
    else:
        return not_found("donor consent(%s)" % consent_id)

    donor_id = None
    if consent.donor_id is not None:
        donor = (
            Donor.query.filter_by(id=consent.donor_id)
            .with_entities(Donor.uuid, Donor.is_locked)
            .first()
        )
        donor_id = consent.donor_id

        if donor:
            if donor.is_locked:
                return locked_response("donor LIMBDON-(%s)" % donor.id)
        else:
            return not_found("related donor")

    withdrawal_date = values.pop("withdrawal_date")
    # Step 1. New Event!
    #
    new_event = Event(
        datetime=withdrawal_date,
        undertaken_by=values.pop("undertaken_by"),
        comments=values.pop("comments"),
        author_id=tokenuser.id,
    )

    try:
        db.session.add(new_event)
        db.session.flush()
        print("new_event.id: ", new_event.id)
    except Exception as err:
        return transaction_error_response(err)

    # Step 2. Modify consent
    consent.withdrawn = True
    consent.is_locked = True
    consent.withdrawal_date = withdrawal_date
    consent.update({"editor_id": tokenuser.id})
    try:
        db.session.add(consent)
        db.session.flush()
    except Exception as err:
        return transaction_error_response(err)

    id = values.pop("donor_id")
    future_consent = values["future_consent"]
    if future_consent:
        old_values = new_consent_schema.dump(consent)
        new_consent = SampleConsent(**old_values)
        new_consent.date = withdrawal_date
        new_consent.comments = (
            new_consent.comments + " | replacement consent for future collection."
        )
        new_consent.author_id = tokenuser.id
        try:
            db.session.add(new_consent)
            db.session.flush()
        except Exception as err:
            return transaction_error_response(err)

        answers = SampleConsentAnswer.query.filter_by(consent_id=consent_id)
        for answer in answers:
            try:
                new_answer = SampleConsentAnswer(
                    consent_id=new_consent.id, question_id=answer.question_id
                )
                new_answer.author_id = tokenuser.id
                db.session.add(new_answer)
                db.session.flush()
            except Exception as err:
                return transaction_error_response(err)

    try:
        new_withdrawal = SampleConsentWithdrawal(**values)
        new_withdrawal.author_id = tokenuser.id
        new_withdrawal.event_id = new_event.id
        if future_consent:
            new_withdrawal.future_consent_id = new_consent.id
    except Exception as err:
        return transaction_error_response(err)

    # Step 4. Step Add disposal instruction
    samples = Sample.query.filter_by(consent_id=consent_id).all()
    for sample in samples:
        new_disposal = SampleDisposal(
            sample_id=sample.id,
            instruction="DES",
            comments="consent withdrawn",
            disposal_date=withdrawal_date,
            approved=True,
            approval_event_id=new_event.id,
            author_id=tokenuser.id,
        )

        try:
            db.session.add(new_disposal)
            db.session.flush()
            sample.disposal_id = new_disposal.id
            sample.update({"editor_id": tokenuser.id})
            db.session.add(sample)
            if future_consent:
                new_withdrawal.future_consent_id = new_consent.id
        except Exception as err:
            return transaction_error_response(err)

    try:
        db.session.commit()
        return success_with_content_response(donor_id)
    except Exception as err:
        return transaction_error_response(err)


@api.route("/donor/consent/LIMBDC-<id>/remove", methods=["POST"])
#@token_required
@requires_roles("data_entry")
def donor_remove_consent(id, tokenuser: UserAccount):
    consent = SampleConsent.query.filter_by(id=id).first()
    if consent:
        if consent.is_locked or consent.withdrawn:
            return locked_response("donor consent! ")
    else:
        return not_found("donor consent(%s)" % id)

    donor_id = None
    if consent.donor_id is not None:
        donor = (
            Donor.query.filter_by(id=consent.donor_id)
            .with_entities(Donor.uuid, Donor.is_locked)
            .first()
        )
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

    msg = ""
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
        return transaction_error_response(msg + " | " + err)


@api.route("/donor/consent/LIMBDC-<id>", methods=["PUT", "GET", "POST"])
@token_required
def donor_consent_view(id, tokenuser: UserAccount):
    return success_with_content_response(
        consent_schema.dump(SampleConsent.query.filter_by(id=id).first())
    )
