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
                         SampleShipment, SampleShipmentToSample, SampleShipmentStatus)

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
    filters, joins = get_filters_and_joins(args, Sample)
    # print('fj: ', filters, joins)

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
    # print(results)
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


def func_update_sample_status(tokenuser: UserAccount, auto_query=True, sample_id=None, sample=None,
                              events={}):
    # - Update sample status when new events added or events are removed!
    # - events: a dictionary of event objects, with keys from the list:
    #  ["sample_disposal", "shipment_status", "shipment_to_sample", "sample_review"]
    #   "shipment_to_sample" can be added only of it is paired with "shipment_status"
    # - auto_query: Boolean, set to True if automated search of relevant objects are needed,
    #                         otherwise update status based on the given objects only.
    # sample_id and sample, the id and the sample object that need to be examined and updated.
    # ########

    if not sample:
        if sample_id:
            sample = Sample.query.filter_by(id=sample_id).first()
    else:
        sample_id = sample.id

    if not sample:
        return {'sample': None, 'message': "Sample/sample_id not found! ", "success": False}

    if sample.is_locked is True or sample.is_closed is True:
        return {'sample': None, 'message': "Sample locked/closed! ", "success": True}

    if events is None or len(events) is 0 :
        auto_query = True
        for e in ["sample_review", "sample_disposal", "disposal_event", "shipment_status"]:
            events[e] = None

    if "shipment_to_sample" in events:
        if "shipment_status" not in events:
            return {'sample': None, 'message': "Shipment_status key missing! ", "success": False}

    if "sample_disposal" in events:
        sample_disposal = events["sample_disposal"]
        if sample_disposal:
            if sample_disposal.sample_id != sample.id:
                return {'sample': None, 'message': "Non-matched sample_review! ", "success": False}
        elif auto_query:
            if sample.disposal_id:
                sample_disposal = SampleDisposal.query.filter_by(id=sample.disposal_id).first()
            else:
                sample_disposal = SampleDisposal.query.join(SampleReview).join(Event).\
                    filter_by(id=sample.disposal_id).order_by(Event.datetime.desc()).first()

        res = {'sample': None, 'message': "No related sample_disposal! ", "success": True}
        if sample_disposal:
            sample.disposal_id = sample_disposal.id
            if sample_disposal.instruction == DisposalInstruction.REV:
                # Pending review
                sample.status = SampleStatus.NRE

            elif sample_disposal.instruction == DisposalInstruction.DES:
                if sample_disposal.protocol_event_id is not None:
                    # sample.status = SampleStatus.DES
                    # sample.is_locked = True
                    # sample.is_closed = True
                    # sample.editor_id = tokenuser.id
                    # sample.updated_on = func.now()
                    sample.update({"is_locked": True, "is_closed": True, "editor_id": tokenuser.id})
                    return {'sample': sample, 'message': "Sample destructed! ", "success": True}

            elif sample_disposal.instruction == DisposalInstruction.TRA:
                if sample_disposal.protocol_event_id is not None:
                    # sample.status = SampleStatus.DES
                    # sample.is_locked = True
                    # sample.is_close = True
                    # sample.status = SampleStatus.TRA
                    # sample.editor_id = tokenuser.id
                    sample.update({"is_locked": True, "is_closed": True, "editor_id": tokenuser.id})
                    return {'sample': sample, 'message': "sample disposed via transfer", "success": True}
            else:
                res = {'sample': None, 'message': "No related sample_disposal for update! ", "success": True}


    if "shipment_status" in events:
        shipment_status = events["shipment_status"]

        shipment_to_sample = None
        if "shipment_to_sample" in events:
            shipment_to_sample = events["shipment_to_sample"]

        if shipment_status and shipment_to_sample:
            if shipment_to_sample.sample_id != sample.id:
                return {'sample': None, 'message': "Non-matched sample id in shipment info! ", "success": False}

        elif auto_query:
            shipment_status = SampleShipmentStatus.query.\
                join(SampleShipmentToSample, SampleShipmentToSample.shipment_id==SampleShipmentStatus.shipment_id).\
                filter(SampleShipmentToSample.sample_id==sample_id).\
                order_by(SampleShipmentStatus.datetime.desc()).first()

        res = {'sample': None, 'message': "No related sample shipment status! ", "success": True}
        if shipment_status:
            if shipment_status.status not in [None, SampleShipmentStatusStatus.TBC]:
                sample.status = SampleStatus.TRA
                shipment = SampleShipment.query.filter_by(id=shipment_status.shipment_id).first_or_404()
                if shipment:
                    sample.current_site_id = shipment.site_id
                else:
                    sample.current_site_id = None

                sample.editor_id = tokenuser.id
                return {"sample": sample, "message": "Sample shipped to site %s !" % sample.current_site_id, "success": True}
            else:
                res = {'sample': None, 'message': "No related sample shipment status for update!", "success": True}


    if "sample_review" in events:
        sample_review = events["sample_review"]
        if sample_review:
            if sample_review.sample_id != sample.id:
                return {'sample': None, 'message': "non matched sample id for review.", 'success': False}
        elif auto_query:
            sample_review = SampleReview.query.join(SampleReview.event).\
                filter_by(sample_id=sample_id).order_by(Event.datetime.desc()).first()

        res = {'sample': None, 'message': "No related sample_review! ", "success": True}
        if sample_review:
            if sample_review.result == ReviewResult.FA:
                if sample_review.review_type == ReviewType.IC:
                    print('Id check!')
                    sample.status = SampleStatus.MIS
                else:
                    sample.status = SampleStatus.UNU
            elif sample_review.result == ReviewResult.PA:
                print('pass!')
                if sample_review.quality == SampleQuality.GOO:
                    sample.status = SampleStatus.AVA
                elif sample_review.quality == SampleQuality.NOT:
                    sample.status = SampleStatus.NRE
            else:
                sample.status = SampleStatus.UNU

            sample.editor_id = tokenuser.id
            return {"sample": sample, "message": "sample updated according to review!", "success": True}

    if not res:
        res = {"sample": None, "message": "No update for sample!", "success": True}
    return res


@api.route("/sample/status/<uuid>", methods=["GET"])
@token_required
def sample_update_sample_status(uuid: str, tokenuser: UserAccount):
    sample = Sample.query.filter_by(uuid=uuid).first()
    if not sample:
        return not_found()

    sample_uuid = sample.uuid
    res = func_update_sample_status(tokenuser=tokenuser,
                                    auto_query=True, sample_id=None,
                                    sample=sample, events={})
    if res["success"]:
        sample = res["sample"]
        if sample:
            try:
                db.session.add(sample)
                db.session.commit()
                #return success_with_content_response(sample_schema.dump(sample))
                return success_with_content_message_response(sample_schema.dump(sample), message=res["message"])
            except Exception as err:
              return transaction_error_response(err)

        else:
            #return not_found()
            return success_with_content_message_response({"uuid": uuid}, message=res["message"])

    else:
        validation_error_response()