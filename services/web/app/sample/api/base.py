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

from flask import request, abort, url_for
from marshmallow import ValidationError
from ...api import api, generics
from ...api.responses import *
from ...api.filters import generate_base_query_filters, get_filters_and_joins

from ...decorators import token_required
from ...misc import get_internal_api_header
from ...webarg_parser import use_args, use_kwargs, parser

from ..views import (
    basic_samples_schema,
    basic_sample_schema,
    sample_protocol_event_schema,
    sample_schema,
    SampleFilterSchema,
    new_fluid_sample_schema,
    sample_type_schema,
    new_cell_sample_schema,
    new_molecular_sample_schema,
    new_sample_schema,

)

from ...database import (db, Sample, SampleToType, SubSampleToSample, UserAccount, Event,
                         SampleProtocolEvent, ProtocolTemplate, SampleDisposal, SampleReview,
                         SampleShipment, SampleShipmentToSample, SampleShipmentStatus,
                         EntityToStorage,
                         SiteInformation, Building, Room, ColdStorage, ColdStorageShelf,
                         DonorToSample)

from sqlalchemy import or_

from ..enums import *

import requests

def sample_protocol_query_stmt(filters_protocol=None, filter_sample_id=None, filters=None, joins=None):
    # Find all parent samples (id) with matching protocol events (by protocol_template_id)
    if filter_sample_id is None:
        subq = db.session.query(Sample.id).filter_by(**filters).filter(*joins).\
            join(SampleProtocolEvent).filter_by(**filters_protocol).subquery()
    else:
        subq = db.session.query(Sample.id).filter(Sample.id.in_(filter_sample_id)). \
            join(SampleProtocolEvent).filter_by(**filters_protocol).subquery()

    protocol_event = db.session.query(ProtocolTemplate).\
        join(SampleProtocolEvent).filter_by(**filters_protocol).first()

    if protocol_event:
        # Protocols of Collection/Study
        if str(protocol_event.type) in ["Collection", "Study", "Temporary Storage"]:

            # Find all sub-samples of the matching samples
            # and take the union of parent and sub-sample ID
            if filter_sample_id is None:
                s2 = db.session.query(Sample.id).filter_by(**filters).filter(*joins).\
                    join(SubSampleToSample, SubSampleToSample.subsample_id == Sample.id).\
                    join(subq, subq.c.id == SubSampleToSample.parent_id)
            else:
                s2 = db.session.query(Sample.id).filter(Sample.id.in_(filter_sample_id)).\
                    join(SubSampleToSample, SubSampleToSample.subsample_id == Sample.id).\
                    join(subq, subq.c.id == SubSampleToSample.parent_id)

            stmt = db.session.query(subq).union(s2)

        else:
            stmt = db.session.query(subq)

    else:
        stmt = db.session.query(subq)

    return (stmt)

def sample_sampletype_query_stmt(filters, joins, filters_sampletype):
    pass
    abort(402)


#@storage.route("/shelf/LIMBSHF-<id>/location", methods=["GET"])
def func_shelf_location(id):
    location = db.session.query(SiteInformation).join(Building).join(Room).join(ColdStorage).\
        join(ColdStorageShelf).with_entities(
            SiteInformation.id, SiteInformation.name,
            Building.id, Building.name,
            Room.id, Room.name,
            ColdStorage.id, ColdStorage.alias,ColdStorage.type,ColdStorage.temp,
            ColdStorageShelf.id, ColdStorageShelf.name).\
        filter(ColdStorageShelf.id==id).first()

    pretty = ""
    if location:
        names = [str(item) for item in location if type(item) is not int]
        pretty = "%s-%s-%s-%s(%s@%s)-%s" % tuple(names)
        colnames = ["site_id", "site_name",
                    "building_id", "building_name",
                    "room_id", "room_name",
                    "coldstorage_id", "coldstorage_name", "coldstorage_type", "coldstorage_temp",
                    "shelf_id", "shelf_name"]
        location = dict(zip(colnames, location))

    return {"location": location, "pretty": pretty}


@api.route("/sample/containers", methods=["GET"])
def sample_get_containers():
    return success_with_content_response(
        {
            "Fluid": {"container": FluidContainer.choices()},
            "Molecular": {"container": FluidContainer.choices()},
            "Cell": {
                "container": CellContainer.choices(),
                "fixation_type": FixationType.choices(),
            },
        }
    )

@api.route("/sample/containertypes", methods=["GET"])
def sample_get_containertypes():
    # Temporary fix for adding containers for long term preservation
    #        TYPE: CellContainer = long term storage
    #        TYPE: FluidContainer = primary container
    # To DO: manage sample type and container info using database
    return success_with_content_response(
        {
            "PRM": {"container": FluidContainer.choices(),
                    "fixation_type": FixationType.choices()},
            "LTS": {"container": CellContainer.choices(),
                    "fixation_type": FixationType.choices()
                    },
        }
    )

@api.route("/sample", methods=["GET"])
@token_required
def sample_home(tokenuser: UserAccount):
    return success_with_content_response(basic_samples_schema.dump(Sample.query.all()))



@api.route("/sample/query", methods=["GET"])
@use_args(SampleFilterSchema(), location="json")
@token_required
def sample_query(args, tokenuser: UserAccount):
    print('args: ', args)
    filters, joins = get_filters_and_joins(args, Sample)
    print('fj: ', filters, joins)

    flag_protocol = False

    if "protocol_id" in filters:
        flag_protocol = True
        protocol_id = filters["protocol_id"]
        filters_protocol = {"protocol_id": protocol_id}
        filters.pop("protocol_id")

    stmt = db.session.query(Sample.id).filter_by(**filters).filter(*joins)

    if flag_protocol:
        stmt = sample_protocol_query_stmt(filters_protocol=filters_protocol, filter_sample_id=stmt)

    stmt = db.session.query(Sample).filter(Sample.id.in_(stmt))
    results = basic_samples_schema.dump(stmt.all())
    return success_with_content_response(
        results
    )


def sample_query_basic(args, tokenuser: UserAccount):
    filters, joins = get_filters_and_joins(args, Sample)
    #print("filters: ", filters)
    #print("joins: ", joins)
    return success_with_content_response(
        basic_samples_schema.dump(
            Sample.query.filter_by(**filters).filter(*joins).all()
        )
    )


@api.route("/sample/<uuid>", methods=["GET"])
@token_required
def sample_view_sample(uuid: str, tokenuser: UserAccount):
    sample = Sample.query.filter_by(uuid=uuid).first()

    if sample:
        return success_with_content_response(sample_schema.dump(sample))
    else:
        return not_found()


@api.route("sample/new", methods=["POST"])
@token_required
def sample_new_sample(tokenuser: UserAccount):
    values = request.get_json()
    # print("values: ", values)
    if not values:
        return no_values_response()

    errors = {}
    for key in [
        "collection_information",
        "disposal_information",
        "sample_information",
        "sample_type_information",
        "consent_information",
    ]:
        if key not in values.keys():
            errors[key] = ["Not found."]

    if len(errors.keys()) > 0:
        return validation_error_response(errors)

    sample_type_response = requests.post(
        url_for(
            "api.sample_new_sample_type",
            base_type=values["sample_information"]["base_type"],
            _external=True,
        ),
        headers=get_internal_api_header(tokenuser),
        json=values["sample_type_information"],
    )

    if sample_type_response.status_code == 200:
        sample_type_information = sample_type_response.json()["content"]

    else:
        return (
            sample_type_response.text,
            sample_type_response.status_code,
            sample_type_response.headers.items(),
        )

    consent_information = values["consent_information"]
    consent_information["id"] = consent_information["consent_id"]

    if "template_id" in values["consent_information"] and "date" in values["consent_information"]:
        consent_response = requests.post(
            url_for("api.sample_new_sample_consent", _external=True),
            headers=get_internal_api_header(tokenuser),
            json=values["consent_information"],
        )

        if consent_response.status_code == 200:
            consent_information = consent_response.json()["content"]
        else:
            return (
                consent_response.text,
                consent_response.status_code,
                consent_response.headers.items(),
            )

    disposal_information = values["disposal_information"]
    disposal_information["id"] = None
    if values["disposal_information"]["instruction"] != "NAP":
        disposal_response = requests.post(
            url_for("api.sample_new_disposal_instructions", _external=True),
            headers=get_internal_api_header(tokenuser),
            json=values["disposal_information"],
        )

        if disposal_response.status_code == 200:
            disposal_information = disposal_response.json()["content"]
        else:
            return (
                disposal_response.text,
                disposal_response.status_code,
                disposal_response.headers.items(),
            )

    sample_information = values["sample_information"]
    sample_information["consent_id"] = consent_information["id"]
    sample_information["sample_to_type_id"] = sample_type_information["id"]
    sample_information["disposal_id"] = disposal_information["id"]

    try:
        sample_values = new_sample_schema.load(sample_information)
    except ValidationError as err:
        return validation_error_response(err)

    new_sample = Sample(**sample_values)
    new_sample.author_id = tokenuser.id
    new_sample.remaining_quantity = sample_values["quantity"]

    try:
        db.session.add(new_sample)
        db.session.commit()
        db.session.flush()
    except Exception as err:
        return transaction_error_response(err)

    values["collection_information"]["sample_id"] = new_sample.id
    sample_id = new_sample.id

    protocol_event_response = requests.post(
        url_for("api.sample_new_sample_protocol_event", _external=True),
        headers=get_internal_api_header(tokenuser),
        json=values["collection_information"],
    )

    if protocol_event_response.status_code == 200:
        collection_event = protocol_event_response.json()["content"]
    else:
        return (
            protocol_event_response.text,
            protocol_event_response.status_code,
            protocol_event_response.headers.items(),
        )

    # DonorToSample
    if "donor_id" in consent_information:
        donor_id = consent_information["donor_id"]
        try:
            dts = DonorToSample(donor_id=donor_id, sample_id=sample_id)
            dts.author_id=tokenuser.id
            db.session.add(dts)
            db.session.commit()
        except Exception as err:
            return transaction_error_response(err)

    return success_with_content_response(
        basic_sample_schema.dump(
            Sample.query.filter_by(id=new_sample.id).first_or_404()
        )
    )



@api.route("sample/new/sample_type_instance/<base_type>", methods=["POST"])
@token_required
def sample_new_sample_type(base_type: str, tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    if base_type == "FLU":
        schema = new_fluid_sample_schema
    elif base_type == "CEL":
        schema = new_cell_sample_schema
    elif base_type == "MOL":
        schema = new_molecular_sample_schema
    else:
        return validation_error_response({"base_type": ["Not a valid base_type."]})


    try:
        new_schema = schema.load(values)
    except ValidationError as err:
        print(err, values)
        return validation_error_response(err)

    sampletotype = SampleToType(**new_schema)
    sampletotype.author_id = tokenuser.id

    db.session.add(sampletotype)

    try:
        db.session.commit()
        db.session.flush()
        return success_with_content_response(sample_type_schema.dump(sampletotype))
    except Exception as err:
        return transaction_error_response(err)


def func_sample_storage_location(sample_id):
    stored_flag = False
    sample_storage = EntityToStorage.query.\
        filter(EntityToStorage.sample_id==sample_id,
               EntityToStorage.removed is not True).\
        order_by(EntityToStorage.entry_datetime.desc()).first()

    sample_storage_info = None
    msg = "No sample storage info! "
    if sample_storage:
        shelf_id = sample_storage.shelf_id

        if shelf_id is None:
            shelf_storage = EntityToStorage.query.filter(EntityToStorage.rack_id==sample_storage.rack_id,
                EntityToStorage.shelf_id!=None, EntityToStorage.removed is not True). \
                order_by(EntityToStorage.entry_datetime.desc()).first()
            if shelf_storage:
                shelf_id = shelf_storage.shelf_id

                sample_storage_info = NewSampleRackToShelfSchema.dump(shelf_storage)
                sample_storage_info["sample_id"] = sample_id
        else:
            sample_storage_info = NewSampleRackToShelfSchema.dump(sample_storage)
            sample_storage_info["sample_id"] = sample_id

        msg = "No sample storage location info! "
        if shelf_id:
            shelf_loc = func_shelf_location(shelf_id)
            if shelf_loc["location"] is not None:
                sample_storage_info.update(shelf_loc["location"])
                msg = "Sample stored in %s! " % shelf_loc["pretty"]

        return {"sample_storage_info": sample_storage_info, "message": msg}



def func_update_sample_status(tokenuser: UserAccount, auto_query=True, sample_id=None, sample=None,
                              events={}):
    # - Update sample status when new events added or events are removed!
    # - events: a dictionary of event objects, with keys from the list:
    #  ["sample_disposal", "sample_storage", "shipment_status", "shipment_to_sample", "sample_review"]
    #   "shipment_to_sample" can be added only of it is paired with "shipment_status"
    # - auto_query: Boolean, set to True if automated search of relevant objects is needed,
    #                         otherwise update status based on the given objects only.
    # sample_id and sample, the id and the sample object that need to be examined and updated.
    # ########
    # TODO refactoring

    if not sample:
        if sample_id:
            sample = Sample.query.filter_by(id=sample_id).first()
    else:
        sample_id = sample.id
    msgs = []
    updated = False
    if not sample:
        msg = "Sample/sample_id not found! "
        res = {'sample': None, 'message': msg, "success": False}

        if "shipment_status" in events and auto_query:
            # involved in multiple samples
            # and user specified event
            msg = "No related samples! "
            shipment_status = events["shipment_status"]

            if shipment_status:
                shipment = SampleShipment.query.filter_by(id=shipment_status.shipment_id).first()
                if not shipment:
                    msg = "Associated shipment not found! "
                    return {'sample': None, 'message': msg, "success": True}

                if shipment.is_locked:
                    msg = "Associated shipment locked! "
                    return {'sample': None, 'message': msg, "success": True}

                subq = db.session.query(SampleShipmentToSample.sample_id).\
                    filter(SampleShipmentToSample.shipment_id==shipment_status.shipment_id)
                samples = Sample.query.filter(Sample.id.in_(subq)).all()
                if not samples:
                    msg = "No involved samples found for the shipment status! "
                    return {'sample': None, 'message': msg, "success": True}

                if shipment_status.status not in [None]: #, "TBC", SampleShipmentStatusStatus.TBC]:
                    updated = True
                    for sample in samples:
                        sample.status = SampleStatus.TRA

                    # if Delievered change the current_site_id to new site
                    if shipment_status.status in ["DEL", SampleShipmentStatusStatus.DEL]:

                        if shipment:
                            for sample in samples:
                                sample.current_site_id = shipment.site_id
                        else:
                            for sample in samples:
                                sample.current_site_id = None

                    for sample in samples:
                        sample.update({"editor_id": tokenuser.id})

                    msg = "%d samples shipped!" % (len(samples))
                    res = {"sample": samples, "message": msg, "success": True}

                else:
                    msg = "No related sample shipment status for update!"
                    res = {'sample': None, 'message': msg, "success": True}

            return res

    if sample.is_locked is True or sample.is_closed is True:
        return {'sample': None, 'message': "Sample locked/closed! ", "success": True}

    if events is None or len(events) is 0:
        auto_query = True
        for e in ["sample_review", "sample_disposal", "disposal_event", "shipment_status", "sample_storage"]:
            events[e] = None

    if "shipment_to_sample" in events:
        if "shipment_status" not in events:
            return {'sample': None, 'message': "Shipment_status key missing! ", "success": False}

    if "sample_disposal" in events:
        sample_disposal = events["sample_disposal"]
        if sample_disposal:
            if sample_disposal.sample_id != sample.id:
                return {'sample': None, 'message': "Non-matched sample_disposal! ", "success": False}
        elif auto_query:
            sample_disposal = SampleDisposal.query.join(SampleReview).join(Event).\
                filter(SampleReview.sample_id==sample_id).order_by(Event.datetime.desc()).first()
            if not sample_disposal:
                # No linked sample review
                # sample_disposal = SampleDisposal.query.filter_by(id=sample.disposal_id).first()
                sample_disposal = SampleDisposal.query.\
                    filter_by(sample_id=sample_id).order_by(SampleDisposal.updated_on.desc()).first()
        msg = "No related sample_disposal! "
        res = {'sample': None, 'message': msg, "success": True}

        if sample_disposal:
            sample.disposal_id = sample_disposal.id
            if sample_disposal.instruction in ['REV', DisposalInstruction.REV]:
                # Pending review
                sample.status = SampleStatus.NRE
                sample.update({"editor_id": tokenuser.id})
                updated = True

            elif sample_disposal.instruction in ['DES', DisposalInstruction.DES]:
                if sample_disposal.disposal_event_id is not None:
                    msg = "Sample destructed! "
                    if sample.status == "DES" or sample.status == SampleStatus.DES:
                        return {'sample': None, 'message': msg, "success": True}

                    sample.status = SampleStatus.DES
                    sample.is_locked = True
                    sample.is_close = True
                    sample.update({"editor_id": tokenuser.id})
                    return {'sample': sample, 'message': msg, "success": True}

            elif sample_disposal.instruction in ["TRA", DisposalInstruction.TRA]:
                if sample_disposal.disposal_event_id is not None:
                    msg = "sample disposed via transfer"
                    if sample.status == "DES" or sample.status == SampleStatus.DES:
                        return {'sample': None, 'message': msg, "success": True}
                    sample.status = SampleStatus.DES
                    sample.is_locked = True
                    sample.is_close = True
                    sample.update({"editor_id": tokenuser.id})
                    return {'sample': sample, 'message': msg, "success": True}
            else:
                msg = "No related sample_disposal for update! "

        msgs.append(msg)

    # current_site_id = None
    stored_flag = False
    if "sample_storage" in events:
        sample_storage = events["sample_storage"]

        if sample_storage:
            if sample_storage.sample_id != sample.id:
                return {'sample': None, 'message': "Non-matched sample id in storage info! ", "success": False}

        elif auto_query:
            sample_storage = EntityToStorage.query.\
                filter(EntityToStorage.sample_id==sample_id,
                       EntityToStorage.removed is not True).\
                order_by(EntityToStorage.entry_datetime.desc()).first()

            msg = "No sample storage info! "
            res = {'sample': None, 'message': msg, "success": True}
            if sample_storage:
                shelf_id = sample_storage.shelf_id
                if shelf_id is None:
                    shelf_storage = EntityToStorage.query.filter(EntityToStorage.rack_id == sample_storage.rack_id,
                        EntityToStorage.shelf_id != None, EntityToStorage.removed is not True). \
                        order_by(EntityToStorage.entry_datetime.desc()).first()
                    if shelf_storage:
                        shelf_id = shelf_storage.shelf_id

                msg = "No sample storage shelf info! "
                res = {'sample': None, 'message': msg, "success": True}
                if shelf_id:
                    shelf_loc = func_shelf_location(shelf_id)

                    if shelf_loc["location"]:
                        if sample.current_site_id != shelf_loc["location"]["site_id"]:
                            sample.current_site_id = shelf_loc["location"]["site_id"]
                            sample.update({"editor_id": tokenuser.id})

                        updated = True
                        stored_flag = True
                        if sample.status in (SampleStatus.TRA, SampleStatus.NCO):
                            sample.status = SampleStatus.NRE

                        msg = "Sample stored in %s! " % shelf_loc["pretty"]

        msgs.append(msg)

    if not stored_flag and "shipment_status" in events:
        shipment_status = events["shipment_status"]
        shipment = None
        shipment_to_sample = None
        if "shipment_to_sample" in events:
            shipment_to_sample = events["shipment_to_sample"]

        if shipment_status and shipment_to_sample:
            if shipment_to_sample.sample_id != sample.id:
                msg = "Non-matched sample id in shipment info! "
                return {'sample': None, 'message': msg, "success": False}
            shipment = SampleShipment.query.filter_by(id=shipment_status.shipment_id, is_locked=False).first()
            if not shipment:
                msg = "No associated open shipment! "
                return {'sample': None, 'message': msg, "success": False}

        elif auto_query:
            shipment_status = SampleShipmentStatus.query.\
                join(SampleShipmentToSample, SampleShipmentToSample.shipment_id==SampleShipmentStatus.shipment_id).\
                join(SampleShipment, SampleShipment.id==SampleShipmentStatus.shipment_id). \
                filter(SampleShipmentToSample.sample_id==sample_id, SampleShipment.is_locked==False).\
                order_by(SampleShipmentStatus.datetime.desc()).first()

        msg = "No related sample shipment status for update! "
        res = {'sample': None, 'message': msg, "success": False}
        if shipment_status:
            if shipment_status.status not in [None]: #, "TBC", SampleShipmentStatusStatus.TBC]:

                if sample.status not in ["TRA", SampleStatus.TRA]:
                    sample.status = SampleStatus.TRA
                    updated = True
                    msg = "Sample transferred!"

                if shipment_status.status in ["DEL", SampleShipmentStatusStatus.DEL]: # Delievered
                    if not shipment:
                        shipment = SampleShipment.query.filter_by(id=shipment_status.shipment_id,
                                                                  is_locked=False).first()
                    if shipment:
                        if sample.current_site_id != shipment.site_id:
                            sample.current_site_id = shipment.site_id
                            updated = True
                            msg = "Sample shipped to site %s !" % sample.current_site_id

            else:
                msg = "No related sample shipment status for update!"

        msgs.append(msg)

    if "sample_review" in events:
        sample_review = events["sample_review"]
        if sample_review:
            if sample_review.sample_id != sample.id:
                return {'sample': None, 'message': "non matched sample id for review.", 'success': False}

        elif auto_query:
            sample_review = SampleReview.query.join(Event).\
                filter(SampleReview.sample_id==sample_id).order_by(Event.datetime.desc()).first()

        msg = "No related sample_review! "
        res = {'sample': None, 'message': msg, "success": True}
        if sample_review:
            if sample_review.result in ['FA', ReviewResult.FA]:

                if sample_review.review_type in ['IC', ReviewType.IC]:
                    sample.status = SampleStatus.MIS
                else:
                    sample.status = SampleStatus.UNU
            elif sample_review.result in ['PA', ReviewResult.PA]:

                if sample_review.quality == SampleQuality.GOO:
                    sample.status = SampleStatus.AVA
                elif sample_review.quality == SampleQuality.NOT:
                    sample.status = SampleStatus.NRE
            else:
                sample.status = SampleStatus.UNU

            updated = True
            msg = "sample updated according to review!"
            res = {"sample": sample, "message": msg, "success": True}

        msgs.append(msg)
        msgs = " | ".join(msgs)
    if updated:
        sample.update({"editor_id": tokenuser.id})
        return {"sample": sample, "message": msgs, "success": True}

    return {"sample": None, "message": "No update for sample!", "success": True}


@api.route("/sample/status/<uuid>", methods=["GET"])
@token_required
def sample_update_sample_status(uuid: str, tokenuser: UserAccount):
    sample = Sample.query.filter_by(uuid=uuid).first()
    if not sample:
        return not_found()

    res = func_update_sample_status(tokenuser=tokenuser,
                                    auto_query=True, sample_id=None,
                                    sample=sample, events={})
    if res["success"]:
        sample = res["sample"]
        if sample:
            try:
                db.session.add(sample)
                db.session.commit()
                return success_with_content_message_response(
                    sample_schema.dump(sample), message=res["message"]
                )
            except Exception as err:
              return transaction_error_response(err)

        else:
            return success_with_content_message_response(
                {"uuid": uuid}, message=res["message"]
            )

    else:
        return validation_error_response(res)