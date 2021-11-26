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
from sqlalchemy.orm.session import make_transient
from ...api import api, generics
from ...api.responses import *
from ...api.filters import generate_base_query_filters, get_filters_and_joins

from ...decorators import token_required
from ...misc import get_internal_api_header
from ...database import (
    db,
    Sample,
    UserAccount,
    SubSampleToSample,
    SampleProtocolEvent,
    SampleToType,
    SampleDisposal,
    Event,
    EntityToStorage
)

from ..views import (
    basic_sample_schema,
    new_sample_schema,
    new_sample_protocol_event_schema,
    new_sample_type_schema,
    new_sample_disposal_schema,
)
from datetime import datetime

from ...webarg_parser import use_args, use_kwargs, parser
import requests

from ...database import db, Sample, UserAccount, SubSampleToSample, UserCart

from ..views import basic_sample_schema, new_sample_schema
from .queries import func_new_sample_type

@api.route("/sample/<uuid>/aliquot", methods=["POST"])
@token_required
def sample_new_aliquot(uuid: str, tokenuser: UserAccount):
    def _validate_values(values: dict) -> bool:
        valid = True
        # print(values)
        for key in [
            "aliquot_date",
            "aliquot_time",
            "aliquots",
            "comments",
            "parent_id",
            "processed_by",
            "processing_protocol",
            "container_base_type",
        ]:
            try:
                values[key]
            except KeyError:
                valid = False
        return valid

    def _validate_aliquots(aliquots: list) -> bool:
        valid = True
        if len(aliquots) == 0:
            return False

        for aliquot in aliquots:
            for key in ["container", "volume", "barcode"]:
                try:
                    aliquot[key]
                except KeyError:
                    valid = False
        return valid

    values = request.get_json()

    if not values:
        return no_values_response()

    if not _validate_values(values):
        return validation_error_response({"messages": "Values failed to validate."})

    if not _validate_aliquots(values["aliquots"]):
        return validation_error_response({"messages": "Failed to load aliquot, sorry."})

    to_remove = sum([float(a["volume"]) for a in values["aliquots"]])
    container_base_type = values["container_base_type"]

    remove_zero_parent_on = values.pop("remove_zero_parent_on", True)

    # Parent Sample Basic Info
    sample = Sample.query.filter_by(uuid=uuid).first_or_404()

    if sample.is_locked or sample.is_closed:
        return locked_response("Parent sample (%s)" % sample.uuid)

    if sample.remaining_quantity <= 0:
        return validation_error_response({"messages": "Insufficient quantity for parent sample!"})

    parent_values = new_sample_schema.dump(sample)
    parent_id = sample.id
    base_type = parent_values["base_type"]

    sample_values = new_sample_schema.load(parent_values)
    remaining_quantity = sample.remaining_quantity

    if remaining_quantity < to_remove:
        return validation_error_response(
            {"messages": "Total sum not equal or less than remaining quantity."}
        )

    # Parent Sample Type/Container
    sampletotype = SampleToType.query.filter_by(
        id=sample.sample_to_type_id
    ).first_or_404()
    type_values = new_sample_type_schema.dump(sampletotype)

    # Parent sample disposal instruction
    disposal_values = None
    if sample.disposal_id:
        sampledisposal = SampleDisposal.query.filter_by(
            id=sample.disposal_id
        ).first_or_404()
        if sampledisposal:
            disposal_values = new_sample_disposal_schema.dump(sampledisposal)

    # New event and sampleprotocol_event
    # each event consists of (i.e. is linked to) a batch of sampleprotocl_event(s) for aliquot
    event_values = {
        "datetime": str(
            datetime.strptime(
                "%s %s" % (values["aliquot_date"], values["aliquot_time"]),
                "%Y-%m-%d %H:%M",  # "%Y-%m-%d %H:%M:%S",
            )
        ),
        "undertaken_by": values["processed_by"],
        "comments": values["comments"],
    }

    try:
        new_event = Event(**event_values)
        new_event.author_id = tokenuser.id
        db.session.add(new_event)
        db.session.flush()
        event_id = new_event.id
    except Exception as err:
        return transaction_error_response(err)

    # TODO: Use existing API endpoint.
    # T1: new protocol event for parent sample
    try:
        new_sample_protocol_event = SampleProtocolEvent(
            sample_id=parent_id,
            protocol_id=values["processing_protocol"],
            event_id=event_id,
        )
        # -- Indicator for protocol event that create new samples
        new_sample_protocol_event.is_locked = True
        new_sample_protocol_event.author_id = tokenuser.id
        db.session.add(new_sample_protocol_event)
        db.session.flush()
    except Exception as err:
        return transaction_error_response(err)

    for aliquot in values["aliquots"]:
        # T2. New sampletotypes for subsamples: store data on sample type and container
        # Keep the sample type and drop the container info from the parent sample
        type_values.pop("fluid_container", None)
        type_values.pop("cellular_container", None)
        type_values.pop("fixation_type", None)

        ali_sampletotype = SampleToType(**type_values)
        ali_sampletotype.id = None

        if container_base_type == "PRM":
            ali_sampletotype.fluid_container = aliquot["container"]

        elif container_base_type == "LTS":
            ali_sampletotype.cellular_container = aliquot["container"]

        if base_type == "CEL":
            if "fixation" in aliquot:
                ali_sampletotype.fixation_type = aliquot["fixation"]

        try:
            db.session.add(ali_sampletotype)
            db.session.flush()
            print("ali_sampletotype id: ", ali_sampletotype.id)

        except Exception as err:
            return transaction_error_response(err)

        # T3.0. New sample_disposal instruction
        disposal_id = None
        if disposal_values:
            sdi = SampleDisposal(**disposal_values)
            sdi.author_id = (tokenuser.id,)

            db.session.add(sdi)
            db.session.flush()
            disposal_id = sdi.id
            print("sample_disposal id: ", disposal_id)

        # T3. New subsamples
        ali_sample = Sample(**sample_values)

        ali_sample.id = None
        ali_sample.uuid = None
        ali_sample.barcode = aliquot["barcode"]
        ali_sample.quantity = float(aliquot["volume"])
        ali_sample.remaining_quantity = float(aliquot["volume"])
        ali_sample.author_id = tokenuser.id
        ali_sample.source = "ALI"
        ali_sample.sample_to_type_id = ali_sampletotype.id
        ali_sample.disposal_id = disposal_id

        try:
            db.session.add(ali_sample)
            db.session.flush()
            # -- Added to sample user cart
            new_ali_uc = UserCart(sample_id=ali_sample.id, selected=True, author_id=tokenuser.id)
            db.session.add(new_ali_uc)
        except Exception as err:
            db.session.rollback()
            return transaction_error_response(err)

        # T4. New subsampletosample
        ssts = SubSampleToSample(
            parent_id=parent_id,
            subsample_id=ali_sample.id,
            protocol_event_id=new_sample_protocol_event.id,
            author_id=tokenuser.id,
        )
        db.session.add(ssts)
        db.session.flush()

    # T4. Update parent sample
    sample.update({"remaining_quantity": sample.remaining_quantity - to_remove,
                   "editor_id": tokenuser.id,
                   #"status": 'UNU',
                   })
    db.session.add(sample)
    new_sample_protocol_event.reduced_quantity = to_remove

    # T5. Remove parent sample if remaining quantity changed to zero!
    if remove_zero_parent_on:
        ets = EntityToStorage.query.filter_by(sample_id=sample.id).all()

        if ets:
            try:
                for et in ets:
                    db.session.delete(et)
                    #et.removed=True
                    #et.update({"editor_id": tokenuser.id})
                    #db.session.add(et)
            except Exception as err:
                db.session.rollback()
                return transaction_error_response(err)

    try:
        db.session.commit()
        flash("Sample Aliquots Added Successfully!" + " Awaiting storage in user cart!!")
    except Exception as err:
        db.session.rollback()
        return transaction_error_response(err)


    return success_with_content_response(
        basic_sample_schema.dump(Sample.query.filter_by(uuid=uuid).first_or_404())
    )


@api.route("/sample/<uuid>/derive", methods=["POST"])
@token_required
def sample_new_derivative(uuid: str, tokenuser: UserAccount):
    def _validate_values(values: dict) -> bool:
        valid = True
        for key in [
            "parent_id",

            "processing_protocol",
            "processing_date",
            "processing_time",
            "processed_by",
            "processing_comments",

            "derivation_protocol",
            "derivation_date",
            "derivation_time",
            "derived_by",
            "derivation_comments",
            "derivatives",
        ]:
            try:
                values[key]
            except KeyError:
                valid = False
        return valid

    def _validate_derivatives(derivatives: list) -> bool:
        valid = True
        if len(derivatives) == 0:
            return False

        for derivative in derivatives:
            for key in ["sample_base_type", "sample_type", "container_base_type", "container_type", "volume", "barcode"]:
                try:
                    derivative[key]
                except KeyError:
                    valid = False
        return valid

    values = request.get_json()
    print("values api", values)
    remove_zero_parent_on = values.pop("remove_zero_parent_on", True)

    if not values:
        return no_values_response()

    if not _validate_values(values):
        return validation_error_response({"messages": "Values failed to validate."})

    if not _validate_derivatives(values["derivatives"]):
        return validation_error_response({"messages": "Failed to load derivatives, sorry."})

    #to_remove = sum([float(a["volume"]) for a in values["derivatives"]])
    # container_base_type = values["container_base_type"]

    # Parent Sample Basic Info
    sample = Sample.query.filter_by(uuid=uuid).first_or_404()

    if sample.is_locked or sample.is_closed:
        return locked_response("Parent sample (%s)" %sample.uuid)

    if sample.remaining_quantity <= 0:
        return validation_error_response({"messages": "Insufficient quantity for parent sample!"})

    parent_values = new_sample_schema.dump(sample)
    parent_id = sample.id

    sample_values = new_sample_schema.load(parent_values)
    # remaining_quantity = 0; #sample.remaining_quantity

    # Parent sample disposal instruction
    disposal_values = None
    if sample.disposal_id:
        sampledisposal = SampleDisposal.query.filter_by(
            id=sample.disposal_id
        ).first_or_404()
        if sampledisposal:
            disposal_values = new_sample_disposal_schema.dump(sampledisposal)

    # T0: New event and sampleprotocol_event for sample processing prior to derivation/aliquot
    if values["processing_protocol"]!= "0":
        processing_event_values = {
            "datetime": str(
                datetime.strptime(
                    "%s %s" % (values["processing_date"], values["processing_time"]),
                    "%Y-%m-%d %H:%M",  # "%Y-%m-%d %H:%M:%S",
                )
            ),
            "undertaken_by": values["processed_by"],
            "comments": values["processing_comments"],
        }

        try:
            new_event1 = Event(**processing_event_values)
            new_event1.author_id = tokenuser.id
            db.session.add(new_event1)
            db.session.flush()
            event1_id = new_event1.id
        except Exception as err:
            return transaction_error_response(err)

        try:
            new_sample_protocol_event1 = SampleProtocolEvent(
                sample_id=parent_id,
                protocol_id=values["processing_protocol"],
                event_id=event1_id,
            )
            # -- Indicator for protocol event that create new samples
            new_sample_protocol_event1.is_locked = False
            new_sample_protocol_event1.author_id = tokenuser.id
            db.session.add(new_sample_protocol_event1)
            db.session.flush()
        except Exception as err:
            return transaction_error_response(err)

    # T1: New event and sampleprotocol_event for parent sample in sample derivation/aliquot event.
    derivation_event_values = {
        "datetime": str(
            datetime.strptime(
                "%s %s" % (values["derivation_date"], values["derivation_time"]),
                "%Y-%m-%d %H:%M",  # "%Y-%m-%d %H:%M:%S",
            )
        ),
        "undertaken_by": values["derived_by"],
        "comments": values["derivation_comments"],
    }

    try:
        new_event2 = Event(**derivation_event_values)
        new_event2.author_id = tokenuser.id
        db.session.add(new_event2)
        db.session.flush()
        event2_id = new_event2.id
    except Exception as err:
        return transaction_error_response(err)

    try:
        new_sample_protocol_event2 = SampleProtocolEvent(
            sample_id=parent_id,
            protocol_id=values["derivation_protocol"],
            event_id=event2_id,
        )
        # -- Indicator for protocol event that create new samples
        new_sample_protocol_event2.is_locked = True
        new_sample_protocol_event2.author_id = tokenuser.id
        new_sample_protocol_event2.reduced_quantity = sample.remaining_quantity

        db.session.add(new_sample_protocol_event2)
        db.session.flush()
    except Exception as err:
        return transaction_error_response(err)

    # T2. New sampletotypes for subsamples/derivatives, linked to the parent sample protocol event
    for derivative in values["derivatives"]:
        der_sampletotype = func_new_sample_type(derivative, tokenuser)
        if isinstance(der_sampletotype, dict):
            if not der_sampletotype["success"]:
                return der_sampletotype

        # T3.0. New sample_disposal instruction
        disposal_id = None
        if disposal_values:
            sdi = SampleDisposal(**disposal_values)
            sdi.author_id=tokenuser.id,

            db.session.add(sdi)
            db.session.flush()
            disposal_id = sdi.id
            print("sample_disposal id: ", disposal_id)

        # T3. New subsamples
        der_sample = Sample(**sample_values)

        der_sample.id = None
        der_sample.uuid = None
        der_sample.barcode = derivative["barcode"]
        der_sample.quantity = float(derivative["volume"])
        der_sample.remaining_quantity = float(derivative["volume"])
        der_sample.source = "DER"
        der_sample.base_type = derivative["sample_base_type"]
        der_sample.sample_to_type_id = der_sampletotype.id
        der_sample.disposal_id = disposal_id
        der_sample.author_id = tokenuser.id

        try:
            db.session.add(der_sample)
            db.session.flush()
            # -- Add to user sample cart
            new_der_uc = UserCart(sample_id=der_sample.id, selected=True, author_id=tokenuser.id)
            db.session.add(new_der_uc)
        except Exception as err:
            db.session.rollback()
            return transaction_error_response(err)

        # T4. New subsampletosample
        ssts = SubSampleToSample(
            parent_id=parent_id,
            subsample_id=der_sample.id,
            protocol_event_id=new_sample_protocol_event2.id,
            author_id=tokenuser.id,
        )
        db.session.add(ssts)
        db.session.flush()


    # T4. Update parent sample
    sample.update({"remaining_quantity": 0,
                   "editor_id": tokenuser.id, #"status": 'UNU'
                   })
    db.session.add(sample)

    # T5. Remove parent sample if remaining quantity changed to zero!
    if remove_zero_parent_on:
        ets = EntityToStorage.query.filter_by(sample_id=sample.id).all()

        if ets:
            try:
                for et in ets:
                    db.session.delete(et)
                    #et.removed=True
                    #et.update({"editor_id": tokenuser.id})
                    #db.session.add(et)
            except Exception as err:
                db.session.rollback()
                return transaction_error_response(err)

    try:
        db.session.commit()
        flash("Sample Derivatives Added Successfully!"+ "Awaiting storage in user cart!!")
    except Exception as err:
        return transaction_error_response(err)

    return success_with_content_response(
        basic_sample_schema.dump(Sample.query.filter_by(uuid=uuid).first_or_404())
    )

