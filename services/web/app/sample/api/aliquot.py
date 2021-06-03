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
)

from ..views import (
    basic_sample_schema,
    new_sample_schema,
    new_sample_protocol_event_schema,
    new_sample_type_schema,
)
from datetime import datetime

from ...webarg_parser import use_args, use_kwargs, parser
import requests

from ...database import db, Sample, UserAccount, SubSampleToSample

from ..views import basic_sample_schema, new_sample_schema


@api.route("/sample/<uuid>/aliquot", methods=["POST"])
@token_required
def sample_new_aliquot(uuid: str, tokenuser: UserAccount):
    def _validate_values(values: dict) -> bool:
        valid = True
        for key in [
            "aliquot_date",
            "aliquot_time",
            "aliquots",
            "comments",
            "parent_id",
            "processed_by",
            "processing_protocol",
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

    # Parent Sample Basic Info
    sample = Sample.query.filter_by(uuid=uuid).first_or_404()

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

    # New sampleprotocol_event
    event_values = {
        "datetime": str(
            datetime.strptime(
                "%s %s" % (values["aliquot_date"], values["aliquot_time"]),
                "%Y-%m-%d %H:%M",  # "%Y-%m-%d %H:%M:%S",
            )
        ),
        "undertaken_by": values["processed_by"],
        "comments": values["comments"],
        "protocol_id": values["processing_protocol"],
        "sample_id": parent_id,
    }

    try:
        event_result = new_sample_protocol_event_schema.load(event_values)
    except ValidationError as err:
        return validation_error_response(err)

    # TODO: Use existing API endpoint.
    # T1: new protocol event for parent sample
    new_event = SampleProtocolEvent(**event_result)
    db.session.add(new_event)
    db.session.flush()

    for aliquot in values["aliquots"]:
        # T2. New sampletotypes for subsamples: store data on sample type and container
        ali_sampletotype = SampleToType(**type_values)
        ali_sampletotype.id = None

        if base_type == "FLU":
            ali_sampletotype.fluid_container = aliquot["container"]
        elif base_type == "CEL":
            ali_sampletotype.cellular_container = aliquot["container"]
            if "fixation" in aliquot:
                ali_sampletotype.fixation_type = aliquot["fixation"]
        elif base_type == "MOL":
            ali_sampletotype.fluid_container = aliquot["container"]

        try:
            db.session.add(ali_sampletotype)
            db.session.flush()
            print("ali_sampletotype id: ", ali_sampletotype.id)

        except Exception as err:
            return transaction_error_response(err)

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

        db.session.add(ali_sample)
        db.session.flush()

        # T4. New subsampletosample
        ssts = SubSampleToSample(
            parent_id=parent_id,
            subsample_id=ali_sample.id,
            author_id=tokenuser.id,
        )
        db.session.add(ssts)
        db.session.flush()

    # T4. Update parent sample
    sample.update({"remaining_quantity": sample.remaining_quantity - to_remove})
    db.session.add(sample)

    try:
        db.session.commit()
        flash("Sample Ailquot Added Successfully!")
    except Exception as err:
        return transaction_error_response(err)

    return success_with_content_response(
        basic_sample_schema.dump(Sample.query.filter_by(uuid=uuid).first_or_404())
    )
