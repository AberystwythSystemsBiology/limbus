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

from ...api import api, generics
from ...api.responses import *

from ...decorators import token_required, check_if_admin, requires_roles

from ...database import (
    db,
    Sample,
    SampleToType,
    SubSampleToSample,
    UserAccount,
    Event,
    SampleProtocolEvent,
    ProtocolTemplate,
    SampleReview,
    SampleDisposalEvent,
    SampleDisposal,
    UserCart,
    SampleShipment,
    SampleShipmentToSample,
    SampleShipmentStatus,
    EntityToStorage,
    SiteInformation,
    Building,
    Room,
    ColdStorage,
    ColdStorageShelf,
    SampleConsent,
    DonorToSample,
    SampleToCustomAttributeData,
    TemporaryStore,
)

from ..views import (
    new_fluid_sample_schema,
    new_cell_sample_schema,
    new_molecular_sample_schema,
    new_sample_protocol_event_schema,
    sample_protocol_event_schema,
    sample_index_schema,
)
from ...tmpstore.views import new_store_schema
from ..enums import SampleSource, DeleteReason
from ...tmpstore.enums import StoreType
import json

def func_new_sample_type(values: dict, tokenuser: UserAccount):

    base_type = values["sample_base_type"]
    if base_type == "FLU":
        sample_type_information = {
            "fluid_type": values["sample_type"],
        }
    elif base_type == "CEL":
        sample_type_information = {
            "cellular_type": values["sample_type"],
            # "tissue_type": values["tissue_sample_type"],
            "fixation_type": values["fixation_type"],
        }
    elif base_type == "MOL":
        sample_type_information = {
            "molecular_type": values["sample_type"],
        }

    if values["container_base_type"] == "PRM":
        sample_type_information.update(
            {
                "fluid_container": values["container_type"],
            }
        )
    else:
        sample_type_information.update(
            {
                "cellular_container": values["container_type"],
            }
        )

    if base_type == "FLU":
        schema = new_fluid_sample_schema
    elif base_type == "CEL":
        schema = new_cell_sample_schema
    elif base_type == "MOL":
        schema = new_molecular_sample_schema
    else:
        return validation_error_response({"base_type": ["Not a valid base_type."]})

    try:
        new_schema = schema.load(sample_type_information)
    except ValidationError as err:
        print(err, values)
        return validation_error_response(err)

    sampletotype = SampleToType(**new_schema)
    sampletotype.author_id = tokenuser.id

    try:
        db.session.add(sampletotype)
        db.session.flush()
        return sampletotype
    except Exception as err:
        return transaction_error_response(err)


def func_new_sample_protocol_event(values, tokenuser: UserAccount):
    # values = request.get_json()

    if not values:
        return no_values_response()

    try:
        event_result = new_sample_protocol_event_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    new_event = Event(**event_result["event"])
    new_event.author_id = tokenuser.id

    try:
        db.session.add(new_event)
        db.session.flush()
    except Exception as err:
        return transaction_error_response(err)

    event_result.pop("event")

    new_sample_protocol_event = SampleProtocolEvent(**event_result)
    new_sample_protocol_event.author_id = tokenuser.id
    new_sample_protocol_event.event_id = new_event.id
    # new_sample_protocol_event.reduced_quantity = reduced_quantity

    sample = Sample.query.filter_by(id=values["sample_id"]).first()
    if not sample:
        return not_found("Sample (%s) ! " % sample.uuid)

    reduced_quantity = values.pop("reduced_quantity", 0)
    if reduced_quantity > 0:
        remaining_quantity = sample.remaining_quantity - reduced_quantity
        if remaining_quantity < 0:
            return validation_error_response(
                {"message": "Reduction quantity > remaining quantity!!!"}
            )

        sample.remaining_quantity = remaining_quantity
        sample.update({"editor_id": tokenuser.id})
        try:
            db.session.add(sample)
        except Exception as err:
            return transaction_error_response(err)

    return new_sample_protocol_event


def func_remove_sampledisposal(sample, tokenuser: UserAccount, msgs=[]):
    success = True
    sds = SampleDisposal.query.filter_by(sample_id=sample.id).all()
    if len(sds) > 0:
        try:
            for sd in sds:
                sample.disposal_id = None
                sample.review_event_id = None
                sd.update({"editor_id": tokenuser.id})
                db.session.delete(sd)
                db.session.flush()
            msgs.append("Sample disposal instructions deleted! ")
        except Exception as err:
            db.session.rollback()
            success = False
            msgs.append(transaction_error_response(err))

    return (success, msgs)


def func_remove_sampledisposalevent(sample, tokenuser: UserAccount, msgs=[]):
    success = True
    sdes = SampleDisposalEvent.query.filter_by(sample_id=sample.id).all()
    if len(sdes) > 0:
        try:
            for sde in sdes:
                # if SampleDisposalEvent.query.filter_by(protocol_event_id=sde.protocol_event_id).count()>1:
                #    sde.protocol_event_id = None
                sde.update({"editor_id": tokenuser.id})
                db.session.delete(sde)
                db.session.flush()
            msgs.append("Sample disposal event deleted! ")
        except Exception as err:
            db.session.rollback()
            success = False
            msgs.append(transaction_error_response(err))
    return (success, msgs)


def func_remove_samplereview(sample, tokenuser: UserAccount, msgs=[]):
    success = True
    srs = SampleReview.query.filter_by(sample_id=sample.id).all()
    if len(srs) > 0:
        try:
            for sr in srs:
                sds = SampleDisposal.query.filter_by(review_event_id=sr.id).all()
                for sd in sds:
                    sd.review_event_id = None
                    sd.update({"editor_id": tokenuser.id})
                    db.session.add(sd)

                sr.update({"editor_id": tokenuser.id})

                if SampleReview.query.filter_by(event_id=sr.event_id).count() > 1:
                    sr.event_id = None

            db.session.delete(sr)
            db.session.flush()
            msgs.append("Sample reviews deleted!")
        except Exception as err:
            db.session.rollback()
            success = False
            msgs.append(transaction_error_response(err))
    return (success, msgs)


def func_remove_sampleshipmenttosample(sample, tokenuser: UserAccount, msgs=[]):
    success = True
    sss = SampleShipmentToSample.query.filter_by(sample_id=sample.id).all()

    if len(sss) > 0:
        try:
            for ss in sss:
                ss.update({"editor_id": tokenuser.id})
                db.session.delete(ss)
                db.session.flush()
            msgs.append("Sample shipment dis-associated")
        except Exception as err:
            db.session.rollback()
            success = False
            msgs.append(transaction_error_response(err))

    return (success, msgs)


def func_remove_sampleprotocolevent(sample, tokenuser: UserAccount, msgs=[]):
    success = True
    pes = SampleProtocolEvent.query.filter_by(sample_id=sample.id).all()
    for pe in pes:
        if SampleProtocolEvent.query.filter_by(event_id=pe.event_id).count() > 1:
            pe.event_id = None
        elif SampleShipment.query.filter_by(event_id=pe.event_id).count() > 0:
            pe.event_id = None

        try:
            pe.update({"editor_id": tokenuser.id})
            db.session.delete(pe)
            db.session.flush()

        except Exception as err:
            db.session.rollback()
            success = False
            msgs.append(transaction_error_response(err))
            return (success, msgs)

    msgs.append(
        "%s Sample protocol events (acquisition/processing/study) deleted!" % len(pes)
    )
    return (success, msgs)


def func_remove_donortosample(sample: Sample, tokenuser: UserAccount, msgs=[]):
    success = True
    dtss = DonorToSample.query.filter_by(sample_id=sample.id).all()
    if len(dtss) > 0:
        try:
            for dts in dtss:
                dts.update({"editor_id": tokenuser.id})
                db.session.delete(dts)
                db.session.flush()
            msgs.append("Sample dis-associated with donor")
        except Exception as err:
            db.session.rollback()
            success = False
            msgs.append(transaction_error_response(err))
    return (success, msgs)


def func_remove_sampleconsent(sample, tokenuser: UserAccount, msgs=[]):
    success = True
    css = SampleConsent.query.filter(
        SampleConsent.id == sample.consent_id, SampleConsent.donor_id is None
    ).all()
    if len(css) > 0:
        try:
            for cs in css:
                if (  # Delete only if oo other samples attached to the consent
                    Sample.query.filter(
                        Sample.consent_id == cs.id, Sample.id != sample.id
                    ).count()
                    == 0
                ):
                    cs.update({"editor_id": tokenuser.id})
                    db.session.delete(cs)

            db.session.flush()
            msgs.append("Orphan sample consent (not linked to any donor) deleted! ")
        except Exception as err:
            db.session.rollback()
            success = False
            msgs.append(transaction_error_response(err))
    return (success, msgs)


def func_remove_sampletocustomattributedata(sample, tokenuser: UserAccount, msgs=[]):
    success = True
    stas = SampleToCustomAttributeData.query.filter_by(sample_id=sample.id).all()
    if len(stas) > 0:
        try:
            for sta in stas:
                sta.update({"editor_id": tokenuser.id})
                db.session.delete(sta)
                db.session.flush()
            msgs.append("Sample custom attribute data deleted")
        except ValidationError as err:
            db.session.rollback()
            success = False
            msgs.append(validation_error_response(err))
    return (success, msgs)


def func_remove_entitytostorage(sample, tokenuser: UserAccount, msgs=[]):
    success = True
    stas = EntityToStorage.query.filter_by(sample_id=sample.id).all()
    if len(stas) > 0:
        try:
            for sta in stas:
                sta.update({"editor_id": tokenuser.id})
                db.session.delete(sta)

            db.session.flush()
            msgs.append("Sample storage data deleted")
        except ValidationError as err:
            db.session.rollback()
            success = False
            msgs.append(validation_error_response(err))
    return (success, msgs)


def func_remove_sampletusercart(sample, tokenuser: UserAccount, msgs=[]):
    success = True
    stas = UserCart.query.filter_by(sample_id=sample.id).all()
    if len(stas) > 0:
        try:
            for sta in stas:
                sta.update({"editor_id": tokenuser.id})
                db.session.delete(sta)

            db.session.flush()
            msgs.append("Sample removed from user cart")
        except ValidationError as err:
            db.session.rollback()
            success = False
            msgs.append(validation_error_response(err))
    return (success, msgs)


def func_remove_sample(sample, tokenuser: UserAccount, msgs=[]):
    success = True
    if sample.is_locked:
        msgs.append(locked_response("sample %s" % sample.uuid))
        return False, msgs

    srs = SampleReview.query.filter_by(sample_id=sample.id)
    if srs.count() > 0:
        msgs.append(in_use_response("sample reviews"))
        return False, msgs

    sms = SampleShipmentToSample.query.filter_by(sample_id=sample.id)
    if sms.count() > 0:
        msgs.append(in_use_response("sample shipments"))
        return False, msgs

    ucs = UserCart.query.filter_by(sample_id=sample.id)
    if ucs.count() > 0:
        msgs.append(in_use_response("sample user cart"))
        return False, msgs

    subs = SubSampleToSample.query.filter_by(parent_id=sample.id)
    if subs.count() > 0:
        msgs.append(
            in_use_response("sub-samples! Delete associated protocol event first!")
        )
        return False, msgs

    subs = SubSampleToSample.query.filter_by(subsample_id=sample.id)
    if subs.count() > 0:
        msgs.append(
            in_use_response("parent-sample! Delete associated protocol event first!")
        )
        return False, msgs

    # Can't be removed unless the only protocol events involved is for sample creation:
    # protocol event is_locked==True
    pes = SampleProtocolEvent.query.filter(
        SampleProtocolEvent.sample_id == sample.id,
        SampleProtocolEvent.is_locked == False,
    )

    if pes.count() > 0:
        msgs.append(in_use_response("protocol events not for initial sample creation!"))
        return False, msgs

    (success, msgs) = func_remove_entitytostorage(sample, tokenuser, msgs)
    if not success:
        return (success, msgs)

    (success, msgs) = func_remove_donortosample(sample, tokenuser, msgs)
    if not success:
        return (success, msgs)

    (success, msgs) = func_remove_sampleconsent(sample, tokenuser, msgs)
    if not success:
        return (success, msgs)

    (success, msgs) = func_remove_sampletocustomattributedata(sample, tokenuser, msgs)
    if not success:
        return (success, msgs)

    try:
        # print("remove sample ", sample.id)
        sample.update({"editor_id": tokenuser.id})
        db.session.delete(sample)
        db.session.flush()
        msgs.append("Sample(%s) deleted!" % sample.uuid)

    except Exception as err:
        db.session.rollback()
        success = False
        msgs.append(transaction_error_response(err))
    return (success, msgs)


def func_remove_aliquot_subsampletosample_children(
    sample, protocol_event, tokenuser: UserAccount, msgs=[]
):
    success = True
    stss = SubSampleToSample.query.filter_by(
        parent_id=sample.id, protocol_event_id=protocol_event.id
    ).all()

    flag_derive = False
    used_qty = 0
    for sts in stss:
        smpl = Sample.query.filter_by(id=sts.subsample_id).first()
        # print('sts id %d , p- %d,  sub- %d ' % (sts.id, sts.parent_id, sts.subsample_id ))
        sts.update({"editor_id": tokenuser.id})
        try:
            db.session.delete(sts)
            db.session.flush()

        except Exception as err:
            db.session.rollback()
            success = False
            msgs.append(transaction_error_response(err))
            return (success, msgs)

        if smpl:
            if smpl.source in ["DER", SampleSource.DER]:
                flag_derive = True

            (success, msgs) = func_remove_sample(smpl, tokenuser, msgs)
            if not success:
                return (success, msgs)
            else:
                used_qty = used_qty + smpl.quantity

    if protocol_event and protocol_event.reduced_quantity > 0:
        sample.remaining_quantity = (
            sample.remaining_quantity + protocol_event.reduced_quantity
        )
    else:
        # - in case of no reduced quantity recorded due to legacy data model
        if flag_derive:
            sample.remaining_quantity = sample.quantity
        else:
            sample.remaining_quantity = used_qty

    try:
        sample.update({"editor_id": tokenuser.id})
        db.session.add(sample)
        db.session.flush()
        msgs.append("All sub-samples dis-associated and deleted! ")

    except Exception as err:
        db.session.rollback()
        success = False
        msgs.append(transaction_error_response(err))
        return (success, msgs)

    print("ali: ", msgs)
    return (success, msgs)


def func_deep_remove_subsampletosample_children(
    sample, protocol_event, tokenuser: UserAccount, msgs=[]
):
    success = True
    if protocol_event is not None:
        stss = SubSampleToSample.query.filter_by(
            parent_id=sample.id, protocol_event_id=protocol_event.id
        ).all()
    else:
        stss = SubSampleToSample.query.filter_by(
            parent_id=sample.id, protocol_event_id=None
        ).all()

    for sts in stss:
        smpl = Sample.query.filter_by(id=sts.subsample_id).first()
        sts.update({"editor_id": tokenuser.id})
        try:
            db.session.delete(sts)
            db.session.flush()

        except ValidationError as err:
            db.session.rollback()
            success = False
            msgs.append(validation_error_response(err))
            return (success, msgs)

        if smpl:
            (success, msgs) = func_deep_remove_sample(smpl, tokenuser, msgs)
            if not success:
                return (success, msgs)

    msgs.append("All %s sub-samples dis-associated and deleted! " % len(stss))
    return (success, msgs)


# def func_root_sample_acquisition_protocol_event(sample_id):
#     sample = Sample.query.filter_by(id=sample_id).first()
#     pe_acq = None
#     if sample is None:
#         success = False
#         msg = "Sample (id=%d) not found" % sample_id
#         return pe_acq, msg
#
#     while sample.source != "NEW":
#         ssts = SubSampleToSample.query.filter_by(subsample_id=sample.id).first()
#         if ssts:
#             sample = Sample.query.filter_by(id=ssts.sample_id).first()
#             if sample is None:
#                 success = False
#                 msg = "Root sample (id=%d) not found" % sample_id
#                 return pe_acq, msg
#         else:
#             success = False
#             msg = "Root sample (id=%d) not found" % sample_id
#             return pe_acq, msg
#
#     pe_acq = SampleProtocolEvent.query.filter_by(sample_id=sample.id).join(
#         ProtocolTemplate, ProtocolTemplate.type == "ACQ"
#     )
#
#     if pe_acq is None:
#         msg = "Root sample (id=%d) acquisition event found!" % sample.id
#     else:
#         msg = "Root sample acquisition event found!"
#     return pe_acq, msg


def func_root_sample(uuid=None, sample=None):

    if sample is None:
        sample = Sample.query.filter_by(uuid=uuid).first()
        if not sample:
            msg = "Sample (id=%d) not found" % uuid
            return None, msg

    while sample.source != SampleSource.NEW:
        ssts = SubSampleToSample.query.filter_by(subsample_id=sample.id).first()
        if ssts:
            sample = Sample.query.filter_by(id=ssts.parent_id).first()
            if sample is None:
                msg = "Root sample (uuid=%s) not found" % uuid
                return None, msg

        else:
            msg = "Root sample (uuid=%s) not found" % uuid
            return None, msg

    if sample.source == SampleSource.NEW:
        msg = "Root sample found: uuid=%s" %sample.uuid
        return sample, msg
    else:
        msg = "Root sample (uuid=%s) not found" % uuid
        return None, msg


@api.route("/sample/<uuid>/update_cache", methods=["GET", "POST"])
@token_required
def sample_update_sample_tmpstore_info(uuid: str, tokenuser: UserAccount):
    if uuid:
        sample = Sample.query.filter_by(uuid=uuid).first()

        if sample is None:
            return not_found("sample %s " % uuid)

    info = sample_index_schema.dump(sample)
    root_sample, msg = func_root_sample(uuid=None, sample=sample)

    if root_sample:
        # print("Root sample: ", root_sample.uuid)
        collection_datetime = (db.session.query(SampleProtocolEvent)
                               .filter(SampleProtocolEvent.sample_id==root_sample.id)
                               .join(ProtocolTemplate, ProtocolTemplate.type == "ACQ")
                               .join(Event)
                               .with_entities(Event.datetime).first()
                               )

        if collection_datetime:
            collection_datetime = collection_datetime[0].strftime("%Y-%m-%d, %H:%M:%S")

        info["collection_datetime"] = collection_datetime
        info["root_sample_uuid"] = root_sample.uuid

    else:
        return validation_error_response(msg)

    tmpstore = TemporaryStore.query.filter_by(uuid=uuid).first()
    if tmpstore:
        # Update entry
        tmpstore.data = info
        tmpstore.type = 'SMPC'
        tmpstore.update({"editor_id": tokenuser.id})

    else:
        # new entry
        values = {}
        values["uuid"] = uuid
        values["type"] = 'SMPC'
        values["data"] = info
        try:
            result = new_store_schema.load(values)
        except ValidationError as err:
            return validation_error_response(err)

        tmpstore = TemporaryStore(**result)
        tmpstore.author_id = tokenuser.id

    try:
        db.session.add(tmpstore)
        db.session.commit()
        message = "Cache info updated successfully!"
        return success_with_content_message_response(info, message)
    except Exception as err:
        db.session.rollback()
        return transaction_error_response(err)


@api.route("/sample/update_collection_id/<first>/<last>", methods=["GET", "POST"])
@api.route("/sample/update_collection_id", methods=["GET", "POST"])
#@token_required
@requires_roles("admin")
def sample_update_collection_id(tokenuser: UserAccount, first=None, last=None):
    pes = ( db.session.query(SampleProtocolEvent)
             .join(ProtocolTemplate, SampleProtocolEvent.protocol_id == ProtocolTemplate.id)
             .join(Sample, Sample.id==SampleProtocolEvent.sample_id)
             .filter(ProtocolTemplate.type == "ACQ")
             .filter(Sample.source=='NEW', Sample.is_closed==False)
             .with_entities(Sample.id, SampleProtocolEvent.id)
             .all()
        )

    first = 0
    last = len(pes)
    if first:
        first = int(first)
    else:
        first = 0

    if last:
        last = int(last)
    else:
        last = len(pes)


    print("total root samples: %d" %len(pes))
    print("first, last ", first, last)
    i = 0
    n_problem = 0
    n=0
    for pe in pes:
        sample_id = pe[0]
        collection_id = pe[1]
        # print(sample_id, collection_id)
        i=i+1
        if i<first:
            continue

        if i>last:
            break

        k = 0
        sample = Sample.query.filter_by(id=sample_id).first()

        if sample and collection_id:
            print(sample.id, collection_id)
            if (sample.collection_id is None):
                sample.collection_id = collection_id
                try:
                    db.session.add(sample)
                    k = k + 1

                except:
                    n_problem = n_problem + 1
                    pass

            consent_id = sample.consent_id
            collection_id = sample.collection_id
            if collection_id:
                subs = (
                    db.session.query(Sample)
                        .join(SampleConsent)#, SampleConsent.id==Sample.consent_id)
                        .filter(Sample.source!='NEW')
                        .filter(Sample.consent_id==consent_id)
                        .distinct(Sample.id)
                        .all()
                    )
                print("subs: ", len(subs))
                for subsample in subs:
                    subsample.collection_id = collection_id
                    try:
                        db.session.add(subsample)
                        k = k+1
                    except:
                        n_problem = n_problem+1
                        pass

            print("k to commit: ", k)
            if k > 0:
                try:
                    db.session.commit()
                    n = n+k
                except:
                    n_problem = n_problem+1

    message = "Successfully updated collection date for %d samples, problems in %d samples" %(n, n_problem)
    print(message)
    return success_with_content_message_response(n, message)



@api.route("/sample/batch_update_cache", methods=["GET", "POST"])
#@token_required
@requires_roles("admin")
def sample_batch_update_sample_tmpstore_info(tokenuser: UserAccount):
    samples = Sample.query.filter_by(is_closed=False).all()
    print("Found samples: ", len(samples))
    n = 0
    n_problem = 0
    for sample in samples:
        uuid = sample.uuid
        info = sample_index_schema.dump(sample)


        root_sample, msg = func_root_sample(uuid=None, sample=sample)

        if root_sample:
            # print("Root sample: ", root_sample.uuid)
            collection_datetime = (db.session.query(SampleProtocolEvent)
                                   .filter(SampleProtocolEvent.sample_id==root_sample.id)
                                   .join(ProtocolTemplate, ProtocolTemplate.type == "ACQ")
                                   .join(Event)
                                   .with_entities(Event.datetime).first()
                                   )

            if collection_datetime:
                collection_datetime=collection_datetime[0].strftime("%Y-%m-%d, %H:%M:%S")

            info["collection_datetime"] = collection_datetime
            info["root_sample_uuid"] = root_sample.uuid

        else:
            n_problem = n_problem + 1
            continue

        tmpstore = TemporaryStore.query.filter_by(uuid=uuid).first()
        if tmpstore:
            # Update entry
            tmpstore.data = info
            tmpstore.update({"editor_id": tokenuser.id})
            tmpstore.type = "SMPC"

        else:
            # new entry
            values = {}
            values["uuid"] = uuid
            values["type"] = 'SMPC'
            values["data"] = info

            try:
                result = new_store_schema.load(values)
            except: # ValidationError as err:
                n_problem = n_problem + 1
                continue
                #return validation_error_response(err)


            tmpstore = TemporaryStore(**result)
            tmpstore.author_id = tokenuser.id

        try:
            db.session.add(tmpstore)
            db.session.flush()

        except: # Exception as err:
            n_problem = n_problem + 1
            continue


        n = n + 1
        if n % 100 == 0:
            # print("n%d: commit" % n)
            try:
                db.session.commit()
            except:
                pass

    try:
        db.session.commit()
    except:
        pass

    message = "Cache info update successful for %d samples!" % n
    message = message + " ; failed for %d samples" %n_problem
    return success_without_content_response(message)



@api.route("/sample/<uuid>/remove", methods=["DELETE", "GET", "POST"])
@token_required
def sample_remove_sample(uuid: str, tokenuser: UserAccount):
    sample = Sample.query.filter_by(uuid=uuid).first()
    if not sample:
        return not_found("sample %s " % uuid)

    values = request.get_json()
    if values is not None:
        comments = "Reason for removal: " + values.pop("comments", "")
        sample.comments = comments

    (success, msgs) = func_remove_sample(sample, tokenuser, [])
    if not success:
        return msgs[-1]

    try:
        db.session.commit()
        msgs.append("Committed successfully!")
        message = " | ".join(msgs)
        return success_with_content_message_response(uuid, message)
    except Exception as err:
        db.session.rollback()
        return transaction_error_response(err)


def func_deep_remove_sample(sample, tokenuser: UserAccount, msgs=[]):
    print("smpl0: ", sample.id)
    protocol_events = SampleProtocolEvent.query.filter_by(sample_id=sample.id).all()
    for protocol_event in protocol_events:
        (success, msgs) = func_deep_remove_subsampletosample_children(
            sample, protocol_event, tokenuser, msgs
        )
        if not success:
            return False, msgs

    # - No protocol event linked (legacy cases)
    (success, msgs) = func_deep_remove_subsampletosample_children(
        sample, None, tokenuser, msgs
    )
    if not success:
        return False, msgs

    (success, msgs) = func_remove_sampledisposal(sample, tokenuser, msgs)
    if not success:
        return False, msgs

    (success, msgs) = func_remove_samplereview(sample, tokenuser, msgs)
    if not success:
        return False, msgs

    (success, msgs) = func_remove_sampledisposalevent(sample, tokenuser, msgs)
    if not success:
        return False, msgs

    (success, msgs) = func_remove_sampleshipmenttosample(sample, tokenuser, msgs)
    if not success:
        return False, msgs

    (success, msg) = func_remove_sampleprotocolevent(sample, tokenuser, msgs)
    if not success:
        return False, msgs

    (success, msgs) = func_remove_donortosample(sample, tokenuser, msgs)
    if not success:
        return False, msgs

    (success, msgs) = func_remove_sampleconsent(sample, tokenuser, msgs)
    if not success:
        return False, msgs

    (success, msgs) = func_remove_sampletocustomattributedata(sample, tokenuser, msgs)
    if not success:
        return False, msgs

    (success, msgs) = func_remove_entitytostorage(sample, tokenuser, msgs)
    if not success:
        return False, msgs

    (success, msgs) = func_remove_sampletusercart(sample, tokenuser, msgs)
    if not success:
        return False, msgs

    try:
        sample.update({"editor_id": tokenuser.id})
        db.session.delete(sample)
        db.session.flush()
        msgs.append("Sample(%s) deleted!" % sample.uuid)

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

    values = request.get_json()
    if values is not None:
        comments = "Reason for removal: " + values.pop("comments", "")
        sample.comments = comments

    subs = SubSampleToSample.query.filter_by(subsample_id=sample.id)
    if subs.count() > 0:
        return in_use_response("parent sample! Delete from the root sample instead!  ")

    (success, msgs) = func_deep_remove_sample(sample, tokenuser, [])
    if not success:
        return msgs[-1]

    try:
        db.session.commit()
        msgs.append("Committed successfully! ")
        message = " | ".join(msgs)
        return success_with_content_message_response(uuid, message)
    except Exception as err:
        db.session.rollback()
        return transaction_error_response(err)


def func_lock_sample_creation_protocolevent(sample_id, tokenuser: UserAccount):
    # pes = SampleProtocolEvent.query.filter_by(sample_id=sample_id, is_locked=True)
    pes = SampleProtocolEvent.query.join(ProtocolTemplate).filter(
        SampleProtocolEvent.sample_id == sample_id,
        SampleProtocolEvent.is_locked == True,
        ProtocolTemplate.type != "ALD",
    )

    if pes.count() > 0:
        msg = "Sample-%s: Already locked!" % sample_id
        return True, msg

    pes = SampleProtocolEvent.query.join(
        SubSampleToSample, SubSampleToSample.protocol_event_id == SampleProtocolEvent.id
    ).filter(
        SubSampleToSample.subsample_id == sample_id,
        SampleProtocolEvent.is_locked == True,
    )
    if pes.count() > 0:
        msg = "Sample-%s: Parent sample protocol event already locked!" % sample_id
        return True, msg

    protocol_event = (
        SampleProtocolEvent.query.join(
            SubSampleToSample,
            SubSampleToSample.protocol_event_id == SampleProtocolEvent.id,
        )
        .filter(
            SubSampleToSample.subsample_id == sample_id,
            SampleProtocolEvent.is_locked == False,
        )
        .order_by(SampleProtocolEvent.created_on.asc())
        .first()
    )

    msg = ""
    if protocol_event:
        msg = (
            "To lock the sample creation event(%s) for its parent sample"
            % protocol_event.id
        )

    else:
        protocol_event = (
            SampleProtocolEvent.query.filter_by(sample_id=sample_id, is_locked=False)
            .order_by(SampleProtocolEvent.created_on.asc())
            .first()
        )
        if protocol_event:
            msg = (
                "To lock the sample creation event (%s) for the sample"
                % protocol_event.id
            )

    if protocol_event:
        protocol_event.is_locked = True
        protocol_event.update({"editor_id": tokenuser.id})
        try:
            db.session.add(protocol_event)
            db.session.commit()
            msg = msg + "Sample-%s: Committed update successfully! " % sample_id
            return True, msg

        except Exception as err:
            db.session.rollback()
            return False, transaction_error_response(err)
    else:
        msg = "Sample-%s: No protocol event for update" % sample_id
        return True, msg


# -- Super Admin functions: TODO
@api.route("/sample/sample_protocol_event_add_reduced_qty", methods=["POST"])
@token_required
def sample_protocol_event_add_reduced_qty(tokenuser: UserAccount):
    if not tokenuser.is_admin:
        return not_allowed()
    # TODO: Go through all protocol event and modify the reduced quantity values


# -- Super Admin functions: TODO: delete it
@api.route("/sample/<uuid>/lock_sample_creation_protocol_event", methods=["POST"])
@token_required
def sample_lock_sample_creation_protocol_event(uuid, tokenuser: UserAccount):
    if not tokenuser.is_admin:
        return not_allowed()

    msgs = []
    if uuid == "all":
        # all aliquote
        pes = (
            SampleProtocolEvent.query.join(ProtocolTemplate)
            .filter(
                SampleProtocolEvent.is_locked == False, ProtocolTemplate.type == "ALD"
            )
            .all()
        )
        for pe in pes:
            pe.is_locked = True
            pe.update({"editor_id": tokenuser.id})
            try:
                db.session.add(pe)
                db.session.commit()
                msgs.append(
                    "Sample-%s aliquot event locked successfully! " % pe.sample_id
                )
            except Exception as err:
                db.session.rollback()
                msg = "Sample-%s aliquot event locked error! " % pe.sample_id
                msg = msg + "(s)" % transaction_error_response(err)["message"]
                msgs.append(msg)

        samples = Sample.query.all()
        if len(samples) == 0:
            return not_found("samples")

        ids_ok = []
        ids_bad = []

        for sample in samples:
            sample_id = sample.id
            [success, msg] = func_lock_sample_creation_protocolevent(
                sample_id, tokenuser
            )
            if success:
                msgs.append(msg)
                ids_ok.append(sample_id)
            else:

                msgs.append(msg["message"])
                ids_bad.append(sample_id)

        return success_with_content_message_response(
            {"ids_ok": ids_ok, "ids_bad": ids_bad}, message=msgs
        )

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
