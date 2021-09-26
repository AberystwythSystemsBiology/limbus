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
from sqlalchemy.sql import func, or_
from marshmallow import ValidationError
from ...api import api, generics

import requests
import json
from ...api.responses import *
from ...decorators import token_required
from ...misc import get_internal_api_header
from ..enums import CartSampleStorageType, SampleShipmentStatusStatus
from .base import func_update_sample_status

from ...database import (
    db,
    SampleShipmentToSample,
    Sample,
    UserCart,
    UserAccount,
    SampleShipment,
    Event,
    EntityToStorage,
    SampleRack,
    SampleShipmentStatus,
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
    sample_shipments_status_schema,
    new_sample_shipment_status_schema,
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

    values = request.get_json()

    if not values:
        return no_values_response()

    if not shipment_event:
        try:
            values['shipment_id'] = shipment.id
            new_shipment_event_values = new_sample_shipment_status_schema.load(values)
        except ValidationError as err:
            return validation_error_response(err)

        shipment_event = SampleShipmentStatus(**new_shipment_event_values)
        shipment_event.author_id = tokenuser.id
        print("status0:", shipment_event.status, type(shipment_event.status), shipment_event.status == SampleShipmentStatusStatus.PRO)
        print('enum status: ', SampleShipmentStatusStatus.PRO)


    else:
        try:
            for attr, value in values.items():
                setattr(shipment_event, attr, value)
        except ValidationError as err:
            return validation_error_response(err)

        shipment_event.updated_on = func.now()
        shipment_event.updated_by = tokenuser.id
        print("status1:", shipment_event.status, shipment_event.status == SampleShipmentStatusStatus.PRO)
        print('enum status: ', SampleShipmentStatusStatus.PRO)


    try:
        db.session.add(shipment_event)

    except Exception as err:
        return transaction_error_response(err)

    sample_status_events = {"shipment_status": shipment_event}
    res = func_update_sample_status(tokenuser=tokenuser, auto_query=True, sample=None, events=sample_status_events)

    message = "Shipment status successfully updated! " + res["message"]
    print("sample", res["message"])

    try:
        if res["success"] is True and res["sample"]:
            for sample in res["sample"]:
                db.session.add(sample)

        db.session.commit()
        return success_with_content_message_response(
            sample_shipment_status_schema.dump(shipment_event), message
        )

    except Exception as err:
        return transaction_error_response(err)

    # try:
    #     db.session.add(shipment_event)
    #     db.session.commit()
    #     return success_with_content_response(sample_shipment_status_schema.dump(shipment_event))
    # except Exception as err:
    #     return transaction_error_response(err)




@api.route("/shipment/view/<uuid>", methods=["GET"])
@token_required
def shipment_view_shipment(uuid: str, tokenuser: UserAccount):
    shipment = SampleShipment.query.filter_by(uuid=uuid).first()

    if not shipment:
        return not_found()

    shipment_event = SampleShipmentStatus.query.filter_by(shipment_id=shipment.id).first()

    if shipment_event:
        return success_with_content_response(
            sample_shipment_status_schema.dump(shipment_event)
        )
    else:

        shipment_info = sample_shipment_schema.dump(shipment)
        shipment_info = {'comments': None,
                         'datetime': shipment_info['created_on'],
                         'tracking_number': None,
                         'shipment': shipment_info,
                         'status': None}
        print('shipment info: ', shipment_info)
        return success_with_content_response(
            shipment_info
        )

@api.route("/shipment/view_samples/<uuid>", methods=["GET"])
@token_required
def shipment_view_shipment_samples(uuid: str, tokenuser: UserAccount):
    shipment = SampleShipment.query.filter_by(uuid=uuid).first()

    if not shipment:
        return not_found()

    shipment_event = SampleShipmentStatus.query.filter_by(shipment_id=shipment.id).first()

    if shipment_event:
        print('shipment status dump: ', sample_shipment_status_schema.dump(shipment_event))
        return success_with_content_response(
            sample_shipment_status_schema.dump(shipment_event)
        )
    else:

        shipment_info = sample_shipment_schema.dump(shipment)
        shipment_info = {'comments': None,
                         'datetime': shipment_info['created_on'],
                         'tracking_number': None,
                         'shipment': shipment_info,
                         'status': None}
        print('shipment info: ', shipment_info)
        return success_with_content_response(
            shipment_info
        )


@api.route("/shipment", methods=["GET"])
@token_required
def shipment_index(tokenuser: UserAccount):
    shipment_data = sample_shipments_status_schema.dump(SampleShipmentStatus.query.all())

    ## No need to check shipments without status if all shipments have a shipment_status
    without_status = db.session.query(SampleShipment).\
        filter(~SampleShipment.id.in_(db.session.query(SampleShipmentStatus.shipment_id)))
    for sm in without_status:
        shipment_data.append({"status":None, "comments":"", "tracking_number":None,"datetime":None,
                              "shipment": sample_shipment_schema.dump(sm)} )

    return success_with_content_response(shipment_data)
    #return basic_sample_shipments_schema.dump(SampleShipment.query.all())



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

    new_shipment_status = SampleShipmentStatus(status=SampleShipmentStatusStatus.TBC,
                            datetime=new_shipment_event_values["event"]["datetime"],
                            shipment_id=new_shipment_event.id)
    db.session.add(new_shipment_status)

    try:

        db.session.query(UserCart).filter_by(author_id=tokenuser.id, selected=True).delete()
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
                {"message": "%s removed from cart" % (uuid)}
            )
        else:
            return success_with_content_response(
                {"message": "%s not in user cart" % (uuid)}
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

        sample_locked = Sample.query.filter_by(id=sample_id, is_locked=True).first()
        if sample_locked:
            msg_locked = "[LIMBSMP-%s]%s" % (sample_locked.id, sample_locked.uuid)
            return locked_response(msg_locked)

        try:
            cart_sample_schema = new_cart_sample_schema.load({"sample_id": sample_id})

        except ValidationError as err:
            return validation_error_response(err)

        ESrecords = EntityToStorage.query.filter_by(sample_id=sample_id).all()

        for es in ESrecords:
            try:
                db.session.delete(es)
                db.session.flush()
                # new_uc.rack_id = es.rack_id
            except Exception as err:
                return transaction_error_response(err)

        new_uc = UserCart.query.filter_by(
            author_id=tokenuser.id, sample_id=sample_id
        ).first()

        if new_uc != None:
            new_uc.selected = True
            new_uc.updated_on = func.now()
            msg = "Sample in the cart selected!"
        else:
            new_uc = UserCart(sample_id=sample_id, storage_type=None, selected=True, author_id=tokenuser.id)
            msg = "Sample added to Cart!"

        try:
            db.session.add(new_uc)
            db.session.commit()
            db.session.flush()

            return success_with_content_message_response(sample_id, message=msg)

        except Exception as err:
            return transaction_error_response(err)
    else:
        return sample_response.content



@api.route("/cart/add/samples", methods=["POST"])
@token_required
def add_samples_to_cart(tokenuser: UserAccount):
    values = request.get_json()
    samples = []
    if values:
        samples = values.pop('samples', [])

    if len(samples) == 0:
        return no_values_response()

    sample_ids = [smpl["id"] for smpl in samples]

    # Site access control
    samples_locked = Sample.query.filter(Sample.id.in_(sample_ids), Sample.is_locked==True).\
        with_entities(Sample.id)

    if tokenuser.account_type != "Administrator":
        samples_other = Sample.query.filter(Sample.id.in_(sample_ids), Sample.is_locked==False,
                    Sample.current_site_id!=None, Sample.current_site_id!=tokenuser.site_id).\
                    with_entities(Sample.id)

        if samples_other.count() > 0:
            samples_locked = samples_locked.union(samples_other)

    # Samples in transit can't be added to cart
    samples_transit = SampleShipmentStatus.query. \
        join(SampleShipmentToSample, SampleShipmentToSample.shipment_id == SampleShipmentStatus.shipment_id). \
        filter(~SampleShipmentStatus.status.in_(["DEL","UND", "CAN"])). \
        with_entities(SampleShipmentToSample.sample_id)

    if samples_transit.count() > 0:
        samples_locked = samples_locked.union(samples_transit)


    if samples_locked.count() > 0:
        samples_locked = samples_locked.distinct().all()
        ids_locked = [sample.id for sample in samples_locked]
        sample_ids = [sample_id for sample_id in sample_ids if sample_id not in ids_locked]
        msg_locked = ' | '.join(["LIMBSMP-%s" % (sample.id) for sample in samples_locked])
    else:
        ids_locked = []
        msg_locked = []

    if len(sample_ids) == 0:
        return locked_response(msg_locked)

    ESRecords = EntityToStorage.query.filter(EntityToStorage.sample_id.in_(sample_ids)).all()
    n_new = 0
    n_old = 0
    if len(ESRecords) > 0:
        try:
            for es in ESRecords:
                db.session.delete(es)
                db.session.flush()
        except Exception as err:
            return transaction_error_response(err)

    for sample_id in sample_ids:

        new_uc = UserCart.query.filter_by(
            author_id=tokenuser.id, sample_id=sample_id
        ).first()

        if new_uc is not None:
            new_uc.selected = True
            new_uc.updated_on = func.now()
            n_old = n_old + 1
        else:
            new_uc = UserCart(sample_id=sample_id, selected=True, author_id=tokenuser.id)
            n_new = n_new + 1

        try:
            db.session.add(new_uc)
            db.session.flush()
        except Exception as err:
            return transaction_error_response(err)

    msg = "%d samples added to Cart!" % n_new
    if (n_old >0 ):
        msg = msg + " | " + "%d samples updated in Cart!" % n_old
    if len(msg_locked) >0:
        msg = msg + " | " +"Locked sample not added: %s" % msg_locked

    try:
        db.session.commit()
        return success_with_content_message_response(sample_ids, message=msg)

    except Exception as err:
        return transaction_error_response(err)

@api.route("/cart/add/samples_racks", methods=["POST"])
@token_required
def add_samples_with_racks_to_cart(tokenuser: UserAccount):
    print(tokenuser.site_id)
    values = request.get_json()
    samples = []
    if values:
        samples = values.pop('samples', [])

    if len(samples) == 0:
        return no_values_response()

    sample_ids = [smpl["id"] for smpl in samples]

    # Site access control
    samples_locked = Sample.query.filter(Sample.id.in_(sample_ids), Sample.is_locked==True).\
        with_entities(Sample.id).all()

    if tokenuser.account_type != "Administrator":
        samples_other = Sample.query.filter(Sample.id.in_(sample_ids), Sample.is_locked==False,
                    Sample.current_site_id != None, Sample.current_site_id!=tokenuser.site_id).\
                    with_entities(Sample.id).all()

        if len(samples_other)>0:
            samples_locked = set(samples_locked).union(set(samples_other))

    # Samples in transit can't be added to cart
    samples_transit = SampleShipmentStatus.query. \
        join(SampleShipmentToSample, SampleShipmentToSample.shipment_id == SampleShipmentStatus.shipment_id). \
        filter(~SampleShipmentStatus.status.in_(["DEL","UND"])). \
        with_entities(SampleShipmentToSample.sample_id).distinct().all()

    if len(samples_transit) > 0:
        samples_locked = set(samples_locked).union(set(samples_transit))


    if len(samples_locked) >0:
        ids_locked = [sample.id for sample in samples_locked]
        sample_ids = [sample_id for sample_id in sample_ids if sample_id not in ids_locked]
        msg_locked = ' | '.join(["LIMBSMP-%s" % (sample.id) for sample in samples_locked])
    else:
        ids_locked = []
        msg_locked = []

    if len(sample_ids) == 0:
        return locked_response(msg_locked)

    for sample_id in sample_ids:
        new_uc = UserCart.query.filter_by(
            author_id=tokenuser.id, sample_id=sample_id
        ).first()

        if new_uc is not None:
            new_uc.selected = True
            new_uc.updated_on = func.now()
            n_old = n_old + 1
        else:
            new_uc = UserCart(sample_id=sample_id, selected=True, author_id=tokenuser.id)
            n_new = n_new + 1

        ets = EntityToStorage.query.filter(sample_id==sample_id,
                        rack_id is not None, removed is not True).\
                    order_by(EntityToStorage.datetime.desc()).first()
        if ets:
            new_uc.rack_id = ets.rack_id
            new_uc.storage_type = "RUC"

        try:
            db.session.add(new_uc)
            db.session.flush()
        except Exception as err:
            return transaction_error_response(err)

    msg = "%d samples added to Cart!" % n_new
    if (n_old >0 ):
        msg = msg + " | " + "%d samples updated in Cart!" % n_old
    if len(msg_locked) >0:
        msg = msg + " | " +"Locked sample not added: %s" % msg_locked

    try:
        db.session.commit()
        return success_with_content_message_response(sample_ids, message=msg)

    except Exception as err:
        return transaction_error_response(err)


@api.route("/cart/add/LIMBRACK-<id>", methods=["POST"])
@token_required
def add_rack_to_cart(id: int, tokenuser: UserAccount):
    rack_response = requests.get(
        url_for("api.storage_rack_view", id=id, _external=True),
        headers=get_internal_api_header(tokenuser),
    )

    # TODO check if rack in transit?
    if rack_response.status_code == 200:
        esCheck = EntityToStorage.query.filter_by(rack_id=id, shelf_id=None).all()
        if esCheck == []:
            return not_found("for the rack with sample(s)")

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
                        {"message": "Sample already added to Cart"}
                    )

                # es = EntityToStorage.query.filter_by(sample_id=es.sample_id).first()
                new_uc = UserCart(sample_id=es.sample_id, rack_id=id,
                                  storage_type=CartSampleStorageType.RUC,
                                  selected=True, author_id=tokenuser.id)
                db.session.add(new_uc)
                db.session.flush()
        try:
            db.session.commit()
            return success_with_content_response({"message": "Sample added to Cart"})

        except Exception as err:
            return transaction_error_response(err)

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