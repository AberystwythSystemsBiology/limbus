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

from flask import request, abort, url_for, flash
from marshmallow import ValidationError
from sqlalchemy import or_
from ...api import api, generics
from ...api.responses import *

from ...decorators import token_required, check_if_admin

from ...database import (db, Sample, SampleToType, SubSampleToSample, UserAccount, Event,
                         SampleProtocolEvent, ProtocolTemplate, SampleReview,
                         SampleDisposalEvent, SampleDisposal,
                         UserCart, SampleShipment, SampleShipmentToSample, SampleShipmentStatus,
                         EntityToStorage,
                         SiteInformation, Building, Room, ColdStorage, ColdStorageShelf,
                         SampleConsent, DonorToSample, SampleToCustomAttributeData)


def func_remove_sampledisposal(sample, msgs=[]):
    success = True
    sds = SampleDisposal.query.filter_by(sample_id=sample.id).all()
    if len(sds)>0:
        try:
            for sd in sds:
                sample.disposal_id = None
                db.session.delete(sd)
                db.session.flush()
            msgs.append('Sample disposal instructions deleted! ')
        except Exception as err:
            db.session.rollback()
            success = False
            msgs.append(transaction_error_response(err))

    return (success, msgs)

def func_remove_sampledisposalevent(sample, msgs=[]):
    success = True
    sdes = SampleDisposalEvent.query.filter_by(sample_id=sample.id).all()
    if len(sdes)>0:
        try:
            for sde in sdes:
                db.session.delete(sde)
                db.session.flush()
            msgs.append('Sample disposal event deleted! ')
        except Exception as err:
            db.session.rollback()
            success = False
            msgs.append(transaction_error_response(err))
    return (success, msgs)

def func_remove_samplereview(sample, msgs=[]):
    success = True
    srs = SampleReview.query.filter_by(sample_id=sample.id).all()
    if len(srs)>0:
        try:
            for sr in srs:
                sd = SampleDisposal.query.filter_by(review_event_id=sr.id).first()
                if sd:
                    sd.review_event_id = None
            db.session.delete(sr)
            db.session.flush()
            msgs.append('Sample reviews deleted!')
        except Exception as err:
            db.session.rollback()
            success = False
            msgs.append(transaction_error_response(err))
    return (success, msgs)



def func_remove_sampleshipmenttosample(sample, msgs=[]):
    success = True
    sss = SampleShipmentToSample.query.filter_by(sample_id=sample.id).all()
    if len(sss) > 0:
        try:
            for ss in sss:
                db.session.delete(ss)
                db.session.flush()
            msgs.append('Sample shipment dis-associated')
        except Exception as err:
            db.session.rollback()
            success = False
            msgs.append(transaction_error_response(err))
    return (success, msgs)

def func_remove_sampleprotocolevent(sample, msgs=[]):
    success = True
    pes = SampleProtocolEvent.query.filter_by(sample_id=sample.id).all()
    if len(pes)>0:
        try:
            for pe in pes:
                db.session.add(pe)
                db.session.flush()
            msgs.append('Sample protocol events (acquisition/processing/study) deleted')
        except Exception as err:
            db.session.rollback()
            success = False
            msgs.append( transaction_error_response(err) )
    return (success, msgs)

def func_remove_donortosample(sample, msgs=[]):
    success = True
    dtss = DonorToSample.query.filter_by(sample_id=sample.id).all()
    if len(dtss) > 0:
        try:
            for dts in dtss:
                db.session.delete(dts)
                db.session.flush()
            msgs.append('Sample dis-associated with donor')
        except Exception as err:
            db.session.rollback()
            success = False
            msgs.append(transaction_error_response(err))
    return (success, msgs)


def func_remove_sampleconsent(sample, msgs=[]):
    success = True
    css = SampleConsent.query.filter(SampleConsent.id==sample.consent_id,
                                     SampleConsent.donor_id is None).all()
    if len(css)>0:
        try:
            for cs in css:
                if Sample.query.filter(consent_id==cs.id, id!=sample.id).count()==0:
                    db.session.delete(cs)
            db.session.flush()
            msgs.append('Orphan sample consent (not linked to any donor) deleted! ')
        except Exception as err:
            db.session.rollback()
            success = False
            msgs.append( transaction_error_response(err))
    return (success, msgs)

def func_remove_sampletocustomattributedata(sample, msgs=[]):
    success = True
    stas = SampleToCustomAttributeData.query.filter_by(sample_id=sample.id).all()
    if len(stas)>0:
        try:
            for sta in stas:
                db.session.delete(sta)
                db.session.flush()
            msgs.append('Sample custom attribute data deleted')
        except ValidationError as err:
            db.session.rollback()
            success = False
            msgs.append(validation_error_response(err))
    return (success, msgs)

def func_remove_sample(sample, msgs=[]):
    success = True
    if sample.is_locked:
        msgs.append(locked_response("sample %s" % sample.uuid))
        return False, msgs

    srs = SampleReview.query.filter_by(sample_id=sample.id)
    if srs.count()>0:
        msgs.append(in_use_response("sample reviews"))
        return False, msgs

    sms = SampleShipmentToSample.query.filter_by(sample_id=sample.id)
    if sms.count()>0:
        msgs.append(in_use_response("sample shipments"))
        return False, msgs

    ucs = UserCart.query.filter_by(sample_id=sample.id)
    if ucs.count()>0:
        msgs.append(in_use_response("sample user cart"))
        return False, msgs

    subs = SubSampleToSample.query.filter_by(parent_id=sample.id)
    if subs.count()>0:
        msgs.append(in_use_response("sub-samples! Delete associated protocol event first!"))
        return False, msgs

    subs = SubSampleToSample.query.filter_by(subsample_id=sample.id)
    if subs.count()>0:
        msgs.append(in_use_response("parent-sample! Delete associated protocol event first!"))
        return False, msgs

    # Can't be removed unless the only protocol events involved is for sample creation:
    # protocol event is_locked==True
    pes = SampleProtocolEvent.query.\
        filter(SampleProtocolEvent.sample_id==sample.id, SampleProtocolEvent.is_locked==False)

    if pes.count()>0:
        msgs.append(in_use_response("protocol events not for initial sample creation!"))
        return False, msgs

    (success, msgs) = func_remove_donortosample(sample, msgs)
    if not success:
       return (success, msgs)
    (success, msgs) = func_remove_sampleconsent(sample, msgs)
    if not success:
        return (success, msgs)
    (success, msgs) = func_remove_sampletocustomattributedata(sample, msgs)
    if not success:
        return (success, msgs)

    try:
        print("remove sample ", sample.id)
        db.session.delete(sample)
        # db.session.flush()
        msgs.append('Sample(%s) deleted!'% sample.uuid)

    except Exception as err:
        db.session.rollback()
        success = False
        msgs.append(transaction_error_response(err))
    return (success, msgs)

def func_remove_aliquot_subsampletosample_children(sample, protocol_event, msgs=[]):
    success = True
    stss = SubSampleToSample.query.filter_by(parent_id=sample.id, protocol_event_id=protocol_event.id).all()
    if len(stss) > 0:
        try:
            print('stss')
            for sts in stss:
                print('sts id %d , p- %d,  sub- %d ' % (sts.id, sts.parent_id, sts.subsample_id ))
                smpl = Sample.query.filter_by(id=sts.subsample_id).first()
                db.session.add(sts)
                db.session.delete(sts)
                db.session.flush()
                if smpl:
                    (success, msgs) = func_remove_sample(smpl, msgs)
                    if not success:
                        return (success, msgs)
                    sample.remaining_quantity = sample.remaining_quantity + smpl.quantity

            db.session.add(sample)
            db.session.flush()
            msgs.append('All sub-samples dis-associated and deleted! ')
        except Exception as err:
            db.session.rollback()
            success = False
            msgs.append(transaction_error_response(err) )
    print('ali: ', msgs)
    return (success, msgs)

def func_deep_remove_subsampletosample_children(sample, protocol_event=None, msgs=[]):
    success = True
    if protocol_event is not None:
        stss = SubSampleToSample.query.filter_by(parent_id=sample.id, protocol_event_id=protocol_event.id).all()
    else:
        stss = SubSampleToSample.query.filter_by(parent_id=sample.id, protocol_event_id=None).all()

    if len(stss) > 0:
        try:
            for sts in stss:
                smpl = Sample.query.filter_by(id=sts.subsample_id).first()
                db.session.delete(sts)
                if smpl:
                    (success, msgs) = func_deep_remove_sample(smpl, msgs)
                    if not success:
                        return (success, msgs)

                db.session.flush()
            msgs.append('All sub-samples dis-associated and deleted! ')
        except ValidationError as err:
            db.session.rollback()
            success = False
            msgs.append(validation_error_response(err))

    return (success, msgs)


@api.route("/sample/<uuid>/remove", methods=["DELETE", "GET", "POST"])
@token_required
def sample_remove_sample(uuid: str, tokenuser: UserAccount):
    sample = Sample.query.filter_by(uuid=uuid).first()
    if not sample:
        return not_found("sample %s " % uuid)

    (success, msgs) = func_remove_sample(sample, [])
    if not success:
        return msgs[-1]

    try:
        db.session.commit()
        msgs.append('Committed successfully!')
        message = " | ".join(msgs)
        return success_with_content_message_response(uuid, message)
    except Exception as err:
        db.session.rollback()
        return transaction_error_response(err)

def func_deep_remove_sample(sample, msgs=[]):
    subs = SubSampleToSample.query.filter_by(subsample_id=sample.id)
    if subs.count()>0:
        msgs.append(in_use_response("parent sample! Delete from the root sample instead!  "))
        return False, msgs
    (success, msgs) = func_remove_sampledisposal(sample, msgs)
    if not success:
        return False, msgs
    (success, msgs) = func_remove_sampledisposalevent(sample, msgs)
    if not success:
        return False, msgs
    (success, msgs) = func_remove_samplereview(sample, msgs)
    if not success:
        return False, msgs

    protocol_events = SampleProtocolEvent.query.filter_by(sample_id=sample.id).all()
    if len(protocol_events)>0:
        for protocol_event in protocol_events:
            (success, msgs) = func_deep_remove_subsampletosample_children(sample, protocol_event, msgs)
            if not success:
                return False, msgs

    # - No protocol event linked (legacy cases)
    (success, msgs) = func_deep_remove_subsampletosample_children(sample, None, msgs)
    if not success:
        return False, msgs

    (success, msgs) = func_remove_sampleshipmenttosample(sample, msgs)
    if not success:
        return False, msgs
    (success, msg) = func_remove_sampleprotocolevent(sample, msgs)
    if not success:
        return False, msgs
    (success, msgs) = func_remove_donortosample(sample, msgs)
    if not success:
       return False, msgs
    (success, msgs) = func_remove_sampleconsent(sample, msgs)
    if not success:
        return False, msgs
    (success, msgs) = func_remove_sampletocustomattributedata(sample, msgs)
    if not success:
        return False, msgs

    try:
        db.session.delete(sample)
        db.session.flush()
        msgs.append('Sample(%s) deleted!'% sample.uuid)

    except Exception as err:
        db.session.rollback()
        success = False
        msgs.append(transaction_error_response(err))
    return (success, msgs)


@api.route("/sample/<uuid>/deep_remove", methods=["DELETE", "GET", "POST"])
@token_required
def sample_deep_remove_sample(uuid: str, tokenuser: UserAccount):
    if not tokenuser.is_admin:
        return not_allowed()

    sample = Sample.query.filter_by(uuid=uuid).first()
    if not sample:
        return not_found("sample %s " % uuid)

    (success, msgs) = func_deep_remove_sample(sample, [])
    if not success:
        return msgs[-1]

    try:
        db.session.commit()
        msgs.append('Committed successfully! ')
        message = " | ".join(msgs)
        return success_with_content_message_response(uuid, message)
    except Exception as err:
        db.session.rollback()
        return transaction_error_response(err)

def func_lock_sample_creation_protocolevent(sample_id, tokenuser: UserAccount):
    # pes = SampleProtocolEvent.query.filter_by(sample_id=sample_id, is_locked=True)
    pes = SampleProtocolEvent.query.join(ProtocolTemplate).\
        filter(SampleProtocolEvent.sample_id==sample_id, SampleProtocolEvent.is_locked==True,
               ProtocolTemplate.type!='ALD')

    if pes.count() > 0:
        msg = "Sample-%s: Already locked!"%sample_id
        return True, msg

    pes = SampleProtocolEvent.query.join(SubSampleToSample,
                                         SubSampleToSample.protocol_event_id == SampleProtocolEvent.id). \
        filter(SubSampleToSample.subsample_id == sample_id, SampleProtocolEvent.is_locked == True)
    if pes.count() > 0:
        msg = "Sample-%s: Parent sample protocol event already locked!"%sample_id
        return True, msg

    protocol_event = SampleProtocolEvent.query.join(SubSampleToSample,
                                                    SubSampleToSample.protocol_event_id == SampleProtocolEvent.id). \
        filter(SubSampleToSample.subsample_id == sample_id, SampleProtocolEvent.is_locked == False). \
        order_by(SampleProtocolEvent.created_on.asc()).first()

    msg = '';
    if protocol_event:
        msg = "To lock the sample creation event(%s) for its parent sample" % protocol_event.id

    else:
        protocol_event = SampleProtocolEvent.query.filter_by(sample_id=sample_id, is_locked=False). \
            order_by(SampleProtocolEvent.created_on.asc()).first()
        if protocol_event:
            msg = "To lock the sample creation event (%s) for the sample" % protocol_event.id

    if protocol_event:
        protocol_event.is_locked = True
        protocol_event.update({"editor_id": tokenuser.id})
        try:
            db.session.add(protocol_event)
            db.session.commit()
            msg = msg + "Sample-%s: Committed update successfully! "%sample_id
            return True, msg

        except Exception as err:
            db.session.rollback()
            return False, transaction_error_response(err)
    else:
        msg = "Sample-%s: No protocol event for update" %sample_id
        return True, msg


# -- Super Admin functions: TODO: delete it
@api.route("/sample/<uuid>/lock_sample_creation_protocol_event", methods=["POST"])
@token_required
def sample_lock_sample_creation_protocol_event(uuid, tokenuser: UserAccount):
    if not tokenuser.is_admin:
        return not_allowed()

    msgs = []
    if uuid == 'all':
        # all aliquote
        pes = SampleProtocolEvent.query.join(ProtocolTemplate).\
            filter(SampleProtocolEvent.is_locked==False, ProtocolTemplate.type=='ALD').all()
        for pe in pes:
            pe.is_locked=True
            pe.update({"editor_id": tokenuser.id})
            try:
                db.session.add(pe)
                db.session.commit()
                msgs.append('Sample-%s aliquot event locked successfully! '%pe.sample_id)
            except Exception as err:
                db.session.rollback()
                msg='Sample-%s aliquot event locked error! ' % pe.sample_id
                msg = msg+ "(s)" % transaction_error_response(err)["message"]
                msgs.append(msg)

        samples = Sample.query.all()
        if len(samples)==0:
            return not_found("samples")

        ids_ok = []
        ids_bad = []

        for sample in samples:
            sample_id = sample.id
            [success, msg] = func_lock_sample_creation_protocolevent(sample_id, tokenuser)
            if success:
                msgs.append(msg)
                ids_ok.append(sample_id)
            else:

                msgs.append(msg["message"])
                ids_bad.append(sample_id)

        #message = "|".join(msgs)
        return success_with_content_message_response({"ids_ok": ids_ok, "ids_bad": ids_bad}, message=msgs)#message)

    else:
        sample = Sample.query.filter_by(uuid=uuid).first()
        if sample is None:
            return not_found("sample")

        sample_id = sample.id
        [success, msg] = func_lock_sample_creation_protocolevent(sample_id, tokenuser)
        if success:
            return success_with_content_message_response(uuid, msg)
        else:
            return msg