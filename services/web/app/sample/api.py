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


from flask import request, abort
from sqlalchemy.orm.session import make_transient
from marshmallow import ValidationError

from ..api import api
from ..api.filters import generate_base_query_filters, get_filters_and_joins
from ..api.responses import *
from ..webarg_parser import use_args, use_kwargs, parser
from ..decorators import token_required
from ..database import (
    db,
    UserAccount,
    Sample,
    SampleConsent,
    SampleConsentAnswer,
    SampleProtocolEvent,
    SampleDisposal,
    SampleToContainer,
    SampleToType,
    SubSampleToSample
)

from .views import (
    basic_samples_schema,
    sample_schema,
    basic_sample_schema,
    new_consent_schema,
    consent_schema,
    new_consent_answer_schema,
    sample_protocol_event_schema,
    new_sample_protocol_event_schema,
    sample_protocol_event_schema,
    new_sample_schema,
    new_sample_disposal_schema,
    basic_disposal_schema,
    new_fluid_sample_schema,
    new_cell_sample_schema,
    sample_type_schema,
    SampleSearchSchema,
)

from datetime import datetime

from .enums import (
    CellContainer,
    FixationType,
    FluidContainer,
)



@api.route("/sample", methods=["GET"])
@token_required
def sample_home(tokenuser: UserAccount):
    return success_with_content_response(
        basic_samples_schema.dump(Sample.query.all())
    )


@api.route("/sample/query", methods=["GET"])
@use_args(SampleSearchSchema(), location="json")
@token_required
def sample_query(args, tokenuser: UserAccount):
    filters, joins = get_filters_and_joins(args, Sample)


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
        return success_with_content_response(
            sample_schema.dump(
                sample
            )
        )
    else:
        abort(404)

@api.route("/sample/new_sample_protocol_event", methods=["POST"])
@token_required
def sample_new_sample_protocol_event(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        event_result = new_sample_protocol_event_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    new_event = SampleProtocolEvent(**event_result)
    new_event.author_id = tokenuser.id

    try:
        db.session.add(new_event)
        db.session.commit()
        db.session.flush()

        return success_with_content_response(
            sample_protocol_event_schema.dump(new_event)
        )

    except Exception as err:
        return transaction_error_response(err)


@api.route("sample/new_sample_type", methods=["POST"])
@token_required
def sample_new_sample_type(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()
    
    try:
        sample_type = values["type"]
        sample_values = values["values"]
    except KeyError as err:
        return validation_error_response(err)
    
    try:
        if sample_type == "FLU":
            sample_schema = new_fluid_sample_schema.load(sample_values)

            new_container = SampleToContainer(
                flui_cont = sample_schema["fluid_container"],
                author_id=tokenuser.id
            )

        elif sample_type == "CEL":
            sample_schema = new_cell_sample_schema.load(sample_values)
            new_container = SampleToContainer(
                cell_cont = sample_schema["cell_container"],
                fixa_cont = sample_schema["fixation_type"],
                author_id=tokenuser.id
            )
        else:
            sample_schema = new_molecular_sample_schema.load(sample_values)
            new_container = SampleToContainer(
                flui_cont = sample_schema["fluid_container"],
                author_id = tokenuser.id
            )
    except ValidationError as err:
        return validation_error_response(err)
    

    db.session.add(new_container)
    db.session.commit()
    db.session.flush()

    if sample_type == "FLU":
        new_sample_to_type = SampleToType(
            flui_type = sample_schema["fluid_sample_type"],
            author_id=tokenuser.id,
            container_id=new_container.id
        )
    elif sample_type == "CEL":
        new_sample_to_type = SampleToType(
            cell_type = sample_schema["cell_sample_type"],
            tiss_type = sample_schema["tissue_sample_type"],
            author_id=tokenuser.id,
            container_id=new_container.id
        )
    else:
        new_sample_to_type = SampleToType(
            molecular_sample_type = sample_schema["mole_type"],
            author_id=tokenuser.id,
            container_id=new_container.id
        )

    db.session.add(new_sample_to_type)
    db.session.commit()
    db.session.flush()

    return success_with_content_response(
        sample_type_schema.dump(new_sample_to_type)
    )



@api.route("sample/new_sample", methods=["POST"])
@token_required
def sample_new_sample(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        sample_values = new_sample_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    new_sample = Sample(**sample_values)
    new_sample.author_id = tokenuser.id
    new_sample.remaining_quantity = sample_values["quantity"]

    try:
        db.session.add(new_sample)
        db.session.commit()
        db.session.flush()

        return success_with_content_response(
            basic_sample_schema.dump(new_sample)
        )
    except Exception as err:
        return transaction_error_response(err)


@api.route("/sample/new_disposal_instructions", methods=["POST"])
@token_required
def sample_new_disposal_instructions(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        disposal_instructions_values = new_sample_disposal_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)


    new_disposal_instructions = SampleDisposal(**disposal_instructions_values)
    new_disposal_instructions.author_id = tokenuser.id

    try:
        db.session.add(new_disposal_instructions)
        db.session.commit()
        db.session.flush()

        return success_with_content_response(
            basic_disposal_schema.dump(new_disposal_instructions)
        )
    except Exception as err:
        return transaction_error_response(err)




@api.route("/sample/containers", methods=["GET"])
def sample_get_containers():
    return success_with_content_response({
        "Fluid": {"container": FluidContainer.choices()},
        "Molecular": {"container": FluidContainer.choices()},
        "Cell": {"container": CellContainer.choices(), "fixation_type": FixationType.choices()}
    })

@api.route("/sample/new_sample_consent", methods=["POST"])
@token_required
def sample_new_sample_consent(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        consent_values = values["consent_data"]
        answer_values = values["answer_data"]

    except KeyError as err:
        return validation_error_response(err)

    try:
        consent_result = new_consent_schema.load(consent_values)
    except ValidationError as err:
        return validation_error_response(err)

    new_consent = SampleConsent(**consent_result)
    new_consent.author_id = tokenuser.id

    try:
        db.session.add(new_consent)
        db.session.commit()
        db.session.flush()
    except Exception as err:
        return transation_error_response(err)

    answers_list = []

    for answer in answer_values:
        try:
            answer_result = new_consent_answer_schema.load(
                {"question_id": answer, "consent_id": new_consent.id}
            )

            answers_list.append(answer_result)

        except ValidationError as err:
            return validation_error_response(err)

    for answer in answers_list:
        try:
            new_answer = SampleConsentAnswer(**answer)
            new_answer.author_id = tokenuser.id
            db.session.add(new_answer)
            db.session.commit()
        except Exception as err:
            return transaction_error_response(err)

    return success_with_content_response(
        consent_schema.dump(SampleConsent.query.filter_by(id=new_consent.id).first())
    )


@api.route("/sample/<uuid>/aliquot", methods=["POST"])
@token_required
def sample_new_aliquot(uuid: str, tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    for i in ["aliquot_date", "aliquot_time", "aliquots", "comments", "parent_id", "processed_by", "processing_protocol_id"]:
        try:
            values[i]
        except KeyError as err:
            transaction_error_response(err)


    to_remove = sum([abs(float(a["volume"])) for a in values["aliquots"]])

    sample = Sample.query.filter_by(uuid=uuid).first_or_404()

    if sample.remaining_quantity < to_remove:
        return "Total amount is greater than remaining", 400

    for aliquot in values["aliquots"]:
        sample_cpy = Sample.query.filter_by(uuid=uuid).first_or_404()
        
        make_transient(sample_cpy)

        sample_cpy.uuid = None
        sample_cpy.id = None
        sample_cpy.barcode = aliquot["barcode"]
        sample_cpy.quantity = aliquot["volume"]
        sample_cpy.remaining_quantity = aliquot["volume"]
        sample_cpy.author_id = tokenuser.id
        sample_cpy.source = "ALI"

        db.session.add(sample_cpy)
        db.session.flush()


        ssts = SubSampleToSample(
            parent_id = sample.id,
            subsample_id = sample_cpy.id
        )

        db.session.add(ssts)
        db.session.commit()

    sample.remaining_quantity = sample.remaining_quantity - to_remove
    db.session.add(sample)
    db.session.commit()

    return success_with_content_response(values)