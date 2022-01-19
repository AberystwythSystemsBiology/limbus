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
    Donor,
    DonorProtocolEvent,
    DonorDiagnosisEvent,
    DonorToSample,
    Event,
    SampleConsent,
    SampleConsentAnswer,
    SampleConsentWithdrawal,
    SampleDisposal,
    Sample,
)

from ...api import api
from ...api.responses import *
from ...api.filters import generate_base_query_filters, get_filters_and_joins
from ...sample.api import func_deep_remove_sample, func_validate_settings
from ...decorators import token_required

from flask import request, current_app, jsonify, send_file
from marshmallow import ValidationError

from sqlalchemy.sql import func
from ...webarg_parser import use_args, use_kwargs, parser


from ...auth.models import UserAccount

from ...donor.views import (
    donor_schema,
    donors_schema,
    new_donor_schema,
    edit_donor_schema,
    basic_donors_schema,
    basic_donor_schema,
    DonorSearchSchema,
    new_donor_diagnosis_event_schema,
    donor_diagnosis_event_schema,
    new_donor_protocol_event_schema,
    # donor_protocol_event_info_schema,
)

from ...event.views import new_event_schema
from ...sample.models import SampleConsent, SampleConsentAnswer, Sample
from ...sample.views import (
    new_consent_schema,
    new_consent_answer_schema,
    consent_schema,
)


def func_remove_donorconsentwithdrawal(donor, tokenuser: UserAccount, msgs=[]):
    success = True
    css = (
        SampleConsentWithdrawal.query.join(
            SampleConsent, SampleConsent.id == SampleConsentWithdrawal.consent_id
        )
        .filter(SampleConsent.donor_id == donor.id)
        .all()
    )
    for cs in css:
        try:
            cs.update({"editor_id": tokenuser.id})
            db.session.delete(cs)
            db.session.flush()

        except Exception as err:
            success = False
            msgs.append(transaction_error_response(err)["message"])
            return (success, msgs)

    msgs.append("Donor consent withdrawal deleted!")
    return (success, msgs)


def func_remove_donorconsent(donor, tokenuser: UserAccount, msgs=[]):
    success = True
    css = SampleConsent.query.filter_by(donor_id=donor.id).all()
    for cs in css:
        ns = Sample.query.filter_by(consent_id=cs.id).count()
        if ns > 0:
            success = False
            msgs.append(in_use_response("%d sample(s)" % ns))
            return (success, msgs)

        nw = SampleConsentWithdrawal.query.filter_by(consent_id=cs.id).count()
        if nw > 0:
            success = False
            msgs.append(in_use_response("sample consent withdrawal"))
            return (success, msgs)

        answers = SampleConsentAnswer.query.filter_by(consent_id=cs.id).all()
        try:
            for answer in answers:
                answer.update({"editor_id": tokenuser.id})
                db.session.delete(answer)

            cs.update({"editor_id": tokenuser.id})
            db.session.delete(cs)
            db.session.flush()

        except Exception as err:
            success = False
            msgs.append(transaction_error_response(err))
            return (success, msgs)

    msgs.append("Donor consent (not linked to any samples) deleted!")
    return (success, msgs)


def func_remove_donordiagnosis(donor, tokenuser, msgs=[]):
    success = True
    stas = DonorDiagnosisEvent.query.filter_by(donor_id=donor.id).all()
    if len(stas) > 0:
        try:
            for sta in stas:
                sta.update({"editor_id": tokenuser.id})
                db.session.delete(sta)
                db.session.flush()
            msgs.append("Deleted %d diagnoses for donor" % len(stas))
        except Exception as err:
            db.session.rollback()
            success = False
            msgs.append(transaction_error_response(err))
    return (success, msgs)


def func_remove_donorprotocolevent(donor, tokenuser: UserAccount, msgs=[]):
    success = True
    stas = DonorProtocolEvent.query.filter_by(donor_id=donor.id).all()

    for sta in stas:
        if DonorProtocolEvent.query.filter_by(event_id=sta.event_id).count() > 1:
            sta.event_id = None

        sta.update({"editor_id": tokenuser.id})
        try:
            db.session.delete(sta)
            db.session.flush()
            msgs.append("Diagnosis deleted for donor")
        except Exception as err:
            db.session.rollback()
            success = False
            msgs.append(transaction_error_response(err))

    return (success, msgs)


def func_remove_donortosample_bydonor(donor: Donor, tokenuser: UserAccount, msgs=[]):
    success = True
    stas = DonorToSample.query.filter_by(donor_id=donor.id).all()

    for sta in stas:

        try:
            sta.update({"editor_id": tokenuser.id})
            db.session.delete(sta)
            db.session.flush()

        except Exception as err:
            db.session.rollback()
            success = False
            msgs.append(transaction_error_response(err))
            return (success, msgs)

    msgs.append("Deleted %s sample links to the donor" % len(stas))
    return (success, msgs)


def func_remove_donor(donor, tokenuser: UserAccount, msgs=[]):
    # Shallow removal without deleting the linked samples
    success = True
    if donor.is_locked:
        msgs.append(locked_response("donor %s" % donor.id))
        return False, msgs

    scs = SampleConsent.query.filter_by(donor_id=donor.id)
    if scs.count() > 0:
        msgs.append(in_use_response("sample consent"))
        return False, msgs

    dpe = DonorProtocolEvent.query.filter_by(donor_id=donor.id)
    if dpe.count() > 0:
        msgs.append(in_use_response("donor protocol event (e.g. linked to a study"))
        return False, msgs

    success, msgs = func_remove_donortosample_bydonor(donor, tokenuser, msgs)
    if not success:
        return (success, msgs)

    success, msgs = func_remove_donordiagnosis(donor, tokenuser, msgs)
    if not success:
        return (success, msgs)

    try:
        print("remove donor ", donor.id)
        donor.update({"editor_id": tokenuser.id})
        db.session.delete(donor)
        db.session.flush()

    except Exception as err:
        db.session.rollback()
        success = False
        msgs.append(transaction_error_response(err))
        return (success, msgs)

    msgs.append("donor(LIMBDON-%s) deleted!" % donor.id)
    return (success, msgs)


def func_deep_remove_donorsamples(donor, tokenuser: UserAccount, msgs=[]):
    success = True
    samples = (
        Sample.query.join(SampleConsent, SampleConsent.id == Sample.consent_id)
        .filter(SampleConsent.donor_id == donor.id)
        .filter(Sample.source == "NEW")
        .all()
    )

    print("n sample:", len(samples))
    for sample in samples:
        # -- deep remove sample will remove sub-samples as well
        success, msgs = func_deep_remove_sample(sample, tokenuser, msgs=msgs)
        if not success:
            return (success, msgs)

    msgs.append("Deep remove samples linked to the donors !")
    return (success, msgs)


def func_deep_remove_donor(donor, tokenuser: UserAccount, msgs=[]):
    # Deep removal
    success = True

    (success, msgs) = func_deep_remove_donorsamples(donor, tokenuser, msgs)
    if not success:
        return (success, msgs)

    (success, msgs) = func_remove_donortosample_bydonor(donor, tokenuser, msgs)
    if not success:
        return (success, msgs)
    (success, msgs) = func_remove_donorconsentwithdrawal(donor, tokenuser, msgs)

    if not success:
        return (success, msgs)
    (success, msgs) = func_remove_donorconsent(donor, tokenuser, msgs)

    if not success:
        return (success, msgs)

    (success, msgs) = func_remove_donorprotocolevent(donor, tokenuser, msgs)
    if not success:
        return (success, msgs)

    (success, msgs) = func_remove_donordiagnosis(donor, tokenuser, msgs)
    if not success:
        return (success, msgs)

    try:
        print("remove donor ", donor.id)
        donor.update({"editor_id": tokenuser.id})
        db.session.delete(donor)
        # db.session.flush()
        msgs.append("donor(LIMBDON-%s) deleted!" % donor.id)

    except Exception as err:
        db.session.rollback()
        success = False
        msgs.append(transaction_error_response(err))

    return (success, msgs)


@api.route("/donor/LIMBDON-<id>/remove", methods=["DELETE", "GET", "POST"])
@token_required
def donor_remove_donor(id, tokenuser: UserAccount):

    donor = Donor.query.filter_by(id=id).first()

    if not donor:
        return not_found("donor LIMBDON-%s" % id)

    if donor.is_locked:
        return locked_response("donor LIMBDON-%s" % id)

    (success, msgs) = func_remove_donor(donor, tokenuser, msgs=[])

    # print("msgs", msgs)
    if not success:
        return msgs[-1]

    try:
        db.session.commit()
        msgs.append("Committed successfully! ")
        message = " | ".join(msgs)
        return success_with_content_message_response("LIMBDON-%s" % id, message)
    except Exception as err:
        db.session.rollback()
        return transaction_error_response(err)


@api.route("/donor/LIMBDON-<id>/deep_remove", methods=["DELETE", "GET", "POST"])
@token_required
def donor_deep_remove_donor(id, tokenuser: UserAccount):
    if not tokenuser.is_admin:
        return validation_error_response("Permission denied!")

    donor = Donor.query.filter_by(id=id).first()
    if not donor:
        return not_found("donor LIMBDON-%s" % id)

    # if donor.is_locked:
    #     return locked_response("donor LIMBDON-%s" % id)

    success, msgs = func_deep_remove_donor(donor, tokenuser, msgs=[])

    if not success:
        return msgs[-1]

    try:
        db.session.commit()
        msgs.append("Committed successfully! ")
        message = " | ".join(msgs)
        return success_with_content_message_response("LIMBDON-%s" % id, message)
    except Exception as err:
        db.session.rollback()
        return transaction_error_response(err)
