# Copyright (C) 2021  Keiron O'Shea <keo7@aber.ac.uk>
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
import requests
import json
from ...api.responses import *
from ...decorators import token_required
from ...misc import get_internal_api_header
from ..enums import CartSampleStorageType, SampleShipmentStatusStatus
from ...database import (
    db,
    SampleShipmentToSample,
    UserCart,
    UserAccount,
    SampleShipment,
    Event,
    EntityToStorage,
    SampleRack,
    SampleShipmentStatus
)

from ..views import (
    user_cart_samples_schema,
    new_cart_sample_schema,
    new_sample_shipment_schema,
    sample_shipment_schema,
    sample_shipment_schema,
    basic_sample_shipments_schema,
    basic_sample_shipment_schema,
    sample_shipment_status_schema,
)


@api.route("/cart", methods=["GET"])
@token_required
def get_cart(tokenuser: UserAccount):
    cart = UserCart.query.filter_by(author_id=tokenuser.id).all()
    return success_with_content_response(user_cart_samples_schema.dump(cart))

@api.route("/shipment/update_status/<uuid>", methods=["PUT"])
@token_required
def shipment_update_status(uuid:str, tokenuser:UserAccount):
    shipment = SampleShipment.query.filter_by(uuid=uuid).first()
    shipment_event = SampleShipmentStatus.query.filter_by(shipment_id=shipment.id).first()

    if not shipment_event:
        return not_found()

    values = request.get_json()

    if not values:
        return no_values_response()
    for attr, value in values.items():
        setattr(shipment_event, attr, value)
    try:
        db.session.add(shipment_event)
        db.session.commit()
        db.session.flush()

        return success_with_content_response(sample_shipment_status_schema.dump(shipment_event))
    except Exception as err:
        return transaction_error_response(err)




@api.route("/shipment/view/<uuid>", methods=["GET"])
@token_required
def shipment_view_shipment(uuid: str, tokenuser: UserAccount):
    shipment = SampleShipment.query.filter_by(uuid=uuid).first()
    shipment_event = SampleShipmentStatus.query.filter_by(shipment_id=shipment.id).first()

    if shipment_event:
        return success_with_content_response(
            sample_shipment_status_schema.dump(shipment_event)
        )
    else:
        return abort(404)


@api.route("/shipment", methods=["GET"])
@token_required
def shipment_index(tokenuser: UserAccount):
    return success_with_content_response(
        basic_sample_shipments_schema.dump(SampleShipment.query.all())
    )


@api.route("/shipment/new", methods=["POST"])
@token_required
def shipment_new_shipment(tokenuser: UserAccount):

    cart = UserCart.query.filter_by(author_id=tokenuser.id,selected=True).all()

    if len(cart) == 0:
        return validation_error_response("No Samples in Cart")

    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        new_shipment_event_values = new_sample_shipment_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    new_event = Event(
        comments = new_shipment_event_values["event"]["comments"],
        undertaken_by = new_shipment_event_values["event"]["undertaken_by"],
        datetime = new_shipment_event_values["event"]["datetime"],
        author_id = tokenuser.id
    )

    try:
        db.session.add(new_event)
        db.session.commit()
        db.session.flush()

    except Exception as err:
        return transaction_error_response(err)

    new_shipment_event = SampleShipment(
        site_id=new_shipment_event_values["site_id"],
        event_id=new_event.id,
        author_id=tokenuser.id
    )
    
    try:
        db.session.add(new_shipment_event)
        db.session.commit()
        db.session.flush()

    except Exception as err:
        return transaction_error_response(err)

    for sample in cart:
        s = sample.sample
        ssets = SampleShipmentToSample(
            sample_id=s.id,
            from_site_id=s.site_id,
            author_id=tokenuser.id,
            shipment_id=new_shipment_event.id,
        )

        db.session.add(ssets)

        s.site_id = new_shipment_event.site_id
        s.editor_id = tokenuser.id

        db.session.add(s)

    new_shipment_status = SampleShipmentStatus(status=SampleShipmentStatusStatus.TBC,datetime=new_shipment_event_values["event"]["datetime"],shipment_id=new_shipment_event.id)
    db.session.add(new_shipment_status)

    try:

        db.session.query(UserCart).filter_by(author_id=tokenuser.id,selected=True).delete()
        db.session.commit()
        db.session.flush()

        return success_with_content_response(
            sample_shipment_schema.dump(new_shipment_event)
        )

    except Exception as err:
        return transaction_error_response(err)


@api.route("/cart/remove/<uuid>", methods=["DELETE"])
@token_required
def remove_sample_from_cart(uuid: str, tokenuser: UserAccount):
    sample_response = requests.get(
        url_for("api.sample_view_sample", uuid=uuid, _external=True),
        headers=get_internal_api_header(tokenuser),
    )

    if sample_response.status_code == 200:
        sample_id = sample_response.json()["content"]["id"]

        uc = UserCart.query.filter_by(
            author_id=tokenuser.id, sample_id=sample_id
        ).first()

        if uc:
            db.session.delete(uc)
            db.session.commit()

            return success_with_content_response(
                {"msg": "%s removed from cart" % (uuid)}
            )
        else:
            return success_with_content_response(
                {"msg": "%s not in user cart" % (uuid)}
            )

    else:
        return sample_response.content

@api.route("/cart/remove/LIMBRACK-<id>", methods=["DELETE"])
@token_required
def remove_rack_from_cart(id: int, tokenuser: UserAccount):
    rack_response = requests.get(
        url_for("api.storage_rack_view", id=id, _external=True),
        headers=get_internal_api_header(tokenuser),
    )

    if rack_response.status_code == 200:
        esRecord = EntityToStorage.query.filter_by(rack_id=id, shelf_id=None).all()
        for es in esRecord:
            uc= UserCart.query.filter_by(author_id=tokenuser.id, sample_id=es.sample_id).first()
            if uc is not None:
                db.session.delete(uc)
                db.session.flush()
        rackRecord = SampleRack.query.filter_by(id=id).first()
        rackRecord.is_locked = False
        try:
            db.session.commit()
        except Exception as err:
            return transaction_error_response(err)
        return success_with_content_response(
                {"msg": " All samples in rack %s removed from cart" % (id)}
            )

    else:
        return success_with_content_response(rack_response.content)


@api.route("/cart/add/<uuid>", methods=["POST"])
@token_required
def add_sample_to_cart(uuid: str, tokenuser: UserAccount):
    sample_response = requests.get(
        url_for("api.sample_view_sample", uuid=uuid, _external=True),
        headers=get_internal_api_header(tokenuser),
    )

    if sample_response.status_code == 200:
        sample_id = sample_response.json()["content"]["id"]
        try:
            cart_sample_schema = new_cart_sample_schema.load({"sample_id": sample_id})

        except ValidationError as err:
            return validation_error_response(err)
        check = UserCart.query.filter_by(
            author_id=tokenuser.id, sample_id=sample_id
        ).first()

        if check != None:
            return success_with_content_response(
                {"msg": "Sample already added to Cart"}
            )

        ESrecords = EntityToStorage.query.filter_by(sample_id=sample_id).all()
        new_uc = UserCart(sample_id=sample_id,storage_type=None,selected=True, author_id=tokenuser.id)

        for es in ESrecords:
            db.session.delete(es)
            db.session.flush()
            # new_uc.rack_id = es.rack_id

        try:
            db.session.add(new_uc)
            db.session.commit()
            db.session.flush()

            return success_with_content_response({"msg": "Sample added to Cart"})

        except Exception as err:
            return transaction_error_response(err)
    else:
        return sample_response.content

@api.route("/cart/add/LIMBRACK-<id>", methods=["POST"])
@token_required
def add_rack_to_cart(id: int, tokenuser: UserAccount):
    rack_response = requests.get(
        url_for("api.storage_rack_view", id=id, _external=True),
        headers=get_internal_api_header(tokenuser),
    )

    if rack_response.status_code == 200:
        esCheck = EntityToStorage.query.filter_by(rack_id=id,shelf_id=None).all()
        if esCheck == []:
            return no_values_response()
        ESRecords = EntityToStorage.query.filter_by(rack_id=id).all()
        rackRecord = SampleRack.query.filter_by(id=id).first()
        rackRecord.is_locked = True
        for es in ESRecords:
            if es.sample_id is None and es.shelf_id is not None:
                db.session.delete(es)
                db.session.flush()
            elif es.sample_id is not None:
                try:
                    cart_sample_schema = new_cart_sample_schema.load({"sample_id": es.sample_id})
                except ValidationError as err:
                    return validation_error_response(err)

                check = UserCart.query.filter_by(
                    author_id=tokenuser.id, sample_id=es.sample_id
                ).first()

                if check != None:
                    return success_with_content_response(
                        {"msg": "Sample already added to Cart"}
                    )

                # es = EntityToStorage.query.filter_by(sample_id=es.sample_id).first()
                new_uc = UserCart(sample_id=es.sample_id,rack_id=id,storage_type=CartSampleStorageType.RUC,selected=True, author_id=tokenuser.id)
                db.session.add(new_uc)
                db.session.flush()
        try:
            db.session.commit()
            return success_with_content_response({"msg": "Sample added to Cart"})

        except Exception as err:
            return transaction_error_response(err)
        # sample_id = sample_response.json()["content"]["id"]


        #
        # if not es is None:
        #         #     new_uc.rack_id = es.rack_id


    else:
        return rack_response.content

@api.route("/cart/select/shipment/LIMBSAMPLE-<sample_id>", methods=["POST"])
@token_required
def select_record_cart_shipment(sample_id: int,tokenuser:UserAccount):
    es_record=EntityToStorage.query.filter_by(sample_id=sample_id).first()
    if es_record is not None and es_record.rack_id is not None:
        sample_records = EntityToStorage.query.filter_by(rack_id=es_record.rack_id, shelf_id=None)
        for sample in sample_records:
            cart_response = requests.post(
                url_for("api.select_record_cart",sample_id=sample.sample_id, _external=True),
                headers=get_internal_api_header(tokenuser),
            )
        return success_without_content_response()
    else:
        cart_response = requests.post(
            url_for("api.select_record_cart",sample_id=sample_id, _external=True),
            headers=get_internal_api_header(tokenuser),
        )
        return success_with_content_response(cart_response.status_code)

@api.route("/cart/select/LIMBSAMPLE-<sample_id>", methods=["POST"])
@token_required
def select_record_cart(sample_id: int, tokenuser: UserAccount):
    ucRecord=UserCart.query.filter_by(sample_id=sample_id).first()
    ucRecord.selected = True
    try:
        db.session.commit()
        return success_without_content_response()

    except Exception as err:
        return transaction_error_response(err)

@api.route("/cart/deselect/shipment/LIMBSAMPLE-<sample_id>", methods=["POST"])
@token_required
def deselect_record_cart_shipment(sample_id: int, tokenuser: UserAccount):
    es_record=EntityToStorage.query.filter_by(sample_id=sample_id).first()
    if es_record is not None and es_record.rack_id is not None:
        sample_records = EntityToStorage.query.filter_by(rack_id=es_record.rack_id, shelf_id=None)
        for sample in sample_records:
            if sample is not None:
                cart_response = requests.post(
                url_for("api.deselect_record_cart",sample_id=sample.sample_id, _external=True),
                    headers=get_internal_api_header(tokenuser)
            )
        return success_without_content_response()

    cart_response = requests.post(
            url_for("api.deselect_record_cart",sample_id=sample_id, _external=True),
            headers=get_internal_api_header(tokenuser)
        )
    return success_with_content_response(cart_response.status_code)

@api.route("/cart/deselect/LIMBSAMPLE-<sample_id>", methods=["POST"])
@token_required
def deselect_record_cart(sample_id: int, tokenuser: UserAccount):
    ucRecord=UserCart.query.filter_by(sample_id=sample_id).first()
    ucRecord.selected = False
    try:
        db.session.commit()
        return success_without_content_response()

    except Exception as err:
        return transaction_error_response(err)