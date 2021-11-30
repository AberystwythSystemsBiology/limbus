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
from sqlalchemy.sql import func, or_, and_
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
    SampleProtocolEvent,
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
def shipment_update_status(uuid: str, tokenuser: UserAccount):
    shipment = SampleShipment.query.filter_by(uuid=uuid).first()
    shipment_event = SampleShipmentStatus.query.filter_by(
        shipment_id=shipment.id
    ).first()

    values = request.get_json()

    if not values:
        return no_values_response()
    print("values", values)
    if not shipment_event:
        try:
            values["shipment_id"] = shipment.id
            new_shipment_event_values = new_sample_shipment_status_schema.load(values)
        except ValidationError as err:
            return validation_error_response(err)

        shipment_event = SampleShipmentStatus(**new_shipment_event_values)
        shipment_event.author_id = tokenuser.id

    else:
        try:
            for attr, value in values.items():
                setattr(shipment_event, attr, value)
        except ValidationError as err:
            return validation_error_response(err)

        shipment_event.updated_on = func.now()
        shipment_event.updated_by = tokenuser.id

    try:
        db.session.add(shipment_event)

    except Exception as err:
        return transaction_error_response(err)

    if values["status"] == "CAN":

        protocol_events = db.session.query(SampleProtocolEvent) \
            .join(SampleShipmentToSample) \
            .filter(SampleShipmentToSample.shipment_id == shipment.id) \
            .all()

        # - Prior to delete protocol event, deassoicate with event, which is used by sampleshipment
        for pe in protocol_events:
            pe.event_id = None
            db.session.add(pe)

        try:
            db.session.flush()
        except Exception as err:
            return transaction_error_response(err)

        for pe in protocol_events:
            db.session.delete(pe)

        try:
            db.session.flush()
        except Exception as err:
            return transaction_error_response(err)

    sample_status_events = {"shipment_status": shipment_event}
    res = func_update_sample_status(
        tokenuser=tokenuser, auto_query=True, sample=None, events=sample_status_events
    )

    message = "Shipment status successfully updated! " + res["message"]

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


@api.route("/shipment/view/<uuid>", methods=["GET"])
@token_required
def shipment_view_shipment(uuid: str, tokenuser: UserAccount):
    shipment = SampleShipment.query.filter_by(uuid=uuid).first()

    if not shipment:
        return not_found()

    shipment_event = SampleShipmentStatus.query.filter_by(
        shipment_id=shipment.id
    ).first()

    if shipment_event:
        return success_with_content_response(
            sample_shipment_status_schema.dump(shipment_event)
        )
    else:

        shipment_info = sample_shipment_schema.dump(shipment)
        shipment_info = {
            "comments": None,
            "datetime": shipment_info["created_on"],
            "tracking_number": None,
            "shipment": shipment_info,
            "status": None,
        }
        # print('shipment info: ', shipment_info)
        return success_with_content_response(shipment_info)


@api.route("/shipment/view_samples/<uuid>", methods=["GET"])
@token_required
def shipment_view_shipment_samples(uuid: str, tokenuser: UserAccount):
    shipment = SampleShipment.query.filter_by(uuid=uuid).first()

    if not shipment:
        return not_found()

    shipment_event = SampleShipmentStatus.query.filter_by(
        shipment_id=shipment.id
    ).first()

    if shipment_event:
        print(
            "shipment status dump: ", sample_shipment_status_schema.dump(shipment_event)
        )
        return success_with_content_response(
            sample_shipment_status_schema.dump(shipment_event)
        )
    else:

        shipment_info = sample_shipment_schema.dump(shipment)
        shipment_info = {
            "comments": None,
            "datetime": shipment_info["created_on"],
            "tracking_number": None,
            "shipment": shipment_info,
            "status": None,
        }
        # print('shipment info: ', shipment_info)
        return success_with_content_response(shipment_info)


@api.route("/shipment", methods=["GET"])
@token_required
def shipment_index(tokenuser: UserAccount):
    shipment_data = sample_shipments_status_schema.dump(
        SampleShipmentStatus.query.all()
    )

    ## No need to check shipments without status if all shipments have a shipment_status
    without_status = db.session.query(SampleShipment).filter(
        ~SampleShipment.id.in_(db.session.query(SampleShipmentStatus.shipment_id))
    )
    for sm in without_status:
        shipment_data.append(
            {
                "status": None,
                "comments": "",
                "tracking_number": None,
                "datetime": None,
                "shipment": sample_shipment_schema.dump(sm),
            }
        )

    return success_with_content_response(shipment_data)


@api.route("/shipment/token_user", methods=["GET"])
@token_required
def shipment_index_tokenuser(tokenuser: UserAccount):
    if tokenuser.is_admin:
        #sm = SampleShipmentStatus.query.all()
        sm = SampleShipmentStatus.query.join(SampleShipment)\
            .join(SampleShipmentToSample)\
            .join(Sample)\
            .filter(
                    Sample.status=='TRA',
                    ~SampleShipmentToSample.id.is_(None),
                    ~SampleShipmentToSample.sample_id.is_(None),
                    )\
            .all()
    else:

        sm = SampleShipmentStatus.query.join(SampleShipment)\
            .join(SampleShipmentToSample)\
            .join(Sample)\
            .filter(Sample.current_site_id==tokenuser.site_id,
                    Sample.status=='TRA',
                    ~SampleShipmentToSample.id.is_(None),
                    ~SampleShipmentToSample.sample_id.is_(None),
                    )\
            .all()

    return success_with_content_response(sample_shipments_status_schema.dump(sm))



@api.route("/shipment/new", methods=["POST"])
@token_required
def shipment_new_shipment(tokenuser: UserAccount):

    cart = UserCart.query.filter_by(author_id=tokenuser.id, selected=True).all()

    if len(cart) == 0:
        return validation_error_response("No Samples in Cart")

    values = request.get_json()
    # print("values", values)
    if not values:
        return no_values_response()

    protocol_id = values.pop("protocol_id")
    try:
        new_shipment_event_values = new_sample_shipment_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)


    new_event = Event(
        comments=new_shipment_event_values["event"]["comments"],
        undertaken_by=new_shipment_event_values["event"]["undertaken_by"],
        datetime=new_shipment_event_values["event"]["datetime"],
        author_id=tokenuser.id,
    )

    try:
        db.session.add(new_event)
        db.session.flush()

    except Exception as err:
        db.session.rollback()
        return transaction_error_response(err)

    new_shipment_event = SampleShipment(
        site_id=new_shipment_event_values["site_id"],
        address_id = new_shipment_event_values["address_id"],
        event_id=new_event.id,
        author_id=tokenuser.id,
    )

    try:
        db.session.add(new_shipment_event)
        db.session.flush()

    except Exception as err:
        db.session.rollback()
        return transaction_error_response(err)

    for sample in cart:
        s = sample.sample

        # -- protocol event for each sample to be transferred. Event shared for all samples
        new_protocol_event = SampleProtocolEvent(
            sample_id=s.id,
            protocol_id=protocol_id,
            event_id=new_event.id,
            reduced_quantity=0,
        )
        new_protocol_event.author_id = tokenuser.id
        new_protocol_event.event_id = new_event.id

        try:
            db.session.add(new_protocol_event)
            db.session.flush()

        except Exception as err:
            return transaction_error_response(err)

        ssets = SampleShipmentToSample(
            sample_id=s.id,
            from_site_id=s.site_id,
            author_id=tokenuser.id,
            shipment_id=new_shipment_event.id,
            protocol_event_id=new_protocol_event.id
        )

        db.session.add(ssets)
        s.status = 'TRA'
        #s.site_id = new_shipment_event.site_id
        s.update({"editor_id": tokenuser.id})

        db.session.add(s)
        db.session.delete(sample)

    new_shipment_status = SampleShipmentStatus(
        status=SampleShipmentStatusStatus.TBC,
        datetime=new_shipment_event_values["event"]["datetime"],
        shipment_id=new_shipment_event.id,
    )
    db.session.add(new_shipment_status)

    try:
        # db.session.query(UserCart).filter_by(
        #     author_id=tokenuser.id, selected=True
        # ).delete()
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
            uc = UserCart.query.filter_by(
                author_id=tokenuser.id, sample_id=es.sample_id
            ).first()
            if uc is not None:
                db.session.delete(uc)
                db.session.flush()
        rackRecord = SampleRack.query.filter_by(id=id).first()
        rackRecord.is_locked = False
        try:
            db.session.commit()
        except Exception as err:
            return transaction_error_response(err)
        return success_with_content_message_response({}, "All samples in rack %s removed from cart" %(id))

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

        sample = Sample.query.filter_by(id=sample_id).first()
        if sample is None:
            return not_found('Sample: %s' %sample_id)
        if sample.is_locked:
            return locked_response('Sample: %s' %sample_id)

        # print('tokenuser.is_admin', tokenuser.is_admin, 'sample_id', sample_id)
        if not tokenuser.is_admin:
            if sample.current_site_id!=None and sample.current_site_id!=tokenuser.site_id:
                return validation_error_response(
                    "Sample in a different site: %s!!" % sample.current_site_id)

        # check if rack is locked?
        rack_locked = db.session.query(EntityToStorage).join(SampleRack, SampleRack.id==EntityToStorage.rack_id). \
                filter(EntityToStorage.sample_id == sample_id, ~EntityToStorage.removed.is_(True),
                       SampleRack.is_locked==True).first()
        if rack_locked:
            return locked_response("associated rack")

        shipment_active = db.session.query(SampleShipment.uuid). \
            join(SampleShipmentToSample, SampleShipment.id==SampleShipmentToSample.shipment_id). \
            filter(SampleShipmentToSample.sample_id==sample.id, SampleShipment.is_locked.is_(False)). \
            first()

        if shipment_active:
            print('shipment_active', shipment_active)
            msg_locked = "The sample is in an active shipment, can only be added to cart from shipment uuid:%s !" % shipment_active[0]
            return validation_error_response(msg_locked)

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
            new_uc = UserCart(
                sample_id=sample_id,
                storage_type=None,
                selected=True,
                author_id=tokenuser.id,
            )
            msg = "Sample added to Cart!"

        try:
            db.session.add(new_uc)
            db.session.commit()
            db.session.flush()

            return success_with_content_message_response(sample_id, message=msg)

        except Exception as err:
            db.session.rollback()
            return transaction_error_response(err)
    else:
        return sample_response.content


@api.route("/cart/add/samples", methods=["POST"])
@token_required
def add_samples_to_cart(tokenuser: UserAccount):
    values = request.get_json()
    samples = []
    if values:
        samples = values.pop("samples", [])

    if len(samples) == 0:
        return no_values_response()

    sample_ids = [smpl["id"] for smpl in samples]
    msg_locked = ""
    # Sample_locked: samples that could not be added to cart for storage/shipment
    #  Sample_locked+Rack_locked+Sample_in_transit
    samples_locked = db.session.query(Sample.id).filter(Sample.id.in_(sample_ids), Sample.is_locked == True)

    # Locked samples union with samples with rack that have been locked
    samples_locked = db.session.query(Sample.id). \
        join(EntityToStorage, EntityToStorage.sample_id == Sample.id). \
        join(SampleRack, SampleRack.id == EntityToStorage.rack_id). \
        filter(Sample.id.in_(sample_ids), Sample.is_locked == False,
               EntityToStorage.removed is not True, SampleRack.is_locked == True).\
        union(samples_locked)
    nlocked = samples_locked.count()
    if nlocked>0:
        msg_locked = msg_locked + ' | %d samples (rack) locked/! '%nlocked

    if not tokenuser.is_admin:
        samples_other = db.session.query(Sample.id).filter(Sample.id.in_(sample_ids), Sample.is_locked==False,
                    Sample.current_site_id.in_([None, tokenuser.site_id]))
        nlocked = samples_other.count()
        if nlocked > 0:

            samples_locked = samples_locked.union(samples_other)
            msg_locked = msg_locked + ' | %d samples current site differs from user! '%nlocked

    # Samples in an open shipment can't be added to cart from sample view, but from shipment
    samples_transit = db.session.query(Sample.id).\
        join(SampleShipmentToSample, SampleShipmentToSample.sample_id == Sample.id). \
        join(SampleShipment, SampleShipment.id == SampleShipmentToSample.shipment_id). \
        filter(Sample.id.in_(sample_ids), Sample.is_locked==False, SampleShipment.is_locked is False)

    nlocked = samples_transit.count()
    if nlocked > 0:
        samples_locked = samples_locked.union(samples_transit)
        msg_locked = msg_locked + ' | %d samples in an open shipment! ' %nlocked

    nlocked = samples_locked.count()
    if nlocked > 0:
        samples_locked = samples_locked.distinct().all()
        ids_locked = [sample[0] for sample in samples_locked]
        sample_ids = [sample_id for sample_id in sample_ids if sample_id not in ids_locked]
        msg_locked = msg_locked + '=> %d samples (cant be added to cart): '%nlocked + ', '.join(["LIMBSMP-%s" % ids_locked])
    else:
        ids_locked = []
        msg_locked = ''

    if len(sample_ids) == 0:
        return validation_error_response(msg_locked)

    ESRecords = EntityToStorage.query.filter(
        EntityToStorage.sample_id.in_(sample_ids)
    ).all()
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
            new_uc.editor_id = tokenuser.id
            new_uc.updated_on = func.now()
            n_old = n_old + 1
        else:
            new_uc = UserCart(
                sample_id=sample_id, selected=True, author_id=tokenuser.id
            )
            n_new = n_new + 1

        try:
            db.session.add(new_uc)
            db.session.flush()
        except Exception as err:
            db.session.rollback()
            return transaction_error_response(err)

    msg = "%d samples added to Cart!" % n_new
    if n_old > 0:
        msg = msg + " | " + "%d samples updated in Cart!" % n_old
    if len(msg_locked) > 0:
        msg = msg + " | " + "Locked sample not added: %s" % msg_locked

    other_ucs = UserCart.query.filter(UserCart.author_id != tokenuser.id, UserCart.sample_id.in_(sample_ids)).all()
    n_other = len(other_ucs)
    if n_other > 0:
        users = [other_uc.author_id for other_uc in other_ucs]
        users = ','.join(list(set(users)))
        try:
            for other_uc in other_ucs:
                db.session.delete(other_uc)
            msg = msg + " | " + "%d samples removed from Cart for other users %s!"%(n_other, users)
        except Exception as err:
            db.session.rollback()
            return transaction_error_response(err)

    try:
        db.session.commit()
        return success_with_content_message_response(sample_ids, message=msg)

    except Exception as err:
        db.session.rollback()
        return transaction_error_response(err)


@api.route("/cart/add/samples_in_shipment", methods=["POST"])
@token_required
def add_samples_in_shipment_to_cart(tokenuser: UserAccount):
    """
    Add samples involved in the shipment to user cart and close (i.e locked) the shipment.
    User will be responsible for storing these transferred samples in the user cart,
    which won't be deletable unless stored.
    """
    values = request.get_json()
    shipment_id = values['id']

    shipment = SampleShipment.query.filter_by(id=shipment_id).first()
    shipment_uuid = shipment.uuid
    if shipment.is_locked:
        return locked_response('Shipment uuid %s' %shipment_uuid)

    sample_ids = [smpl['sample_id'] for smpl in values['involved_samples']]
    print('sample_ids', sample_ids)

    if len(sample_ids)==0:
        return not_found('the involved samples for shipment uuid: %s', shipment_uuid)

    # Sample_locked: samples that could not be added to cart for storage/shipment
    #  Sample_locked+Rack_locked+Sample_in_transit
    msg_locked = '';
    samples_locked = db.session.query(Sample.id).filter(Sample.id.in_(sample_ids), Sample.is_locked==True)
    nlocked = samples_locked.count()
    if nlocked>0:
        msg_locked = msg_locked + ' | %d Sample locked! ' % nlocked;


    if not tokenuser.is_admin:
        # Can only add samples of same site as for the operator
        samples_other = db.session.query(Sample.id).filter(Sample.id.in_(sample_ids), Sample.is_locked.is_(False),
                                                           Sample.current_site_id.in_([None, tokenuser.site_id]))

        n_other = samples_other.count()
        if n_other > 0:
            samples_locked = samples_locked.union(samples_other)
            msg_locked = msg_locked + '| Current site different from the user for %d samples! ' % n_other

    # Samples in transit can't be added to cart
    samples_transit = (
        db.session.query(SampleShipmentToSample.sample_id)
        .join(
            SampleShipmentStatus,
            SampleShipmentToSample.shipment_id == SampleShipmentStatus.shipment_id,
        )
        .filter(
            ~SampleShipmentStatus.status.in_(["DEL", "UND", "CAN"]),
            SampleShipmentToSample.sample_id.in_(sample_ids),
        )
    )

    n_transit = samples_transit.count()
    if n_transit>0:
        samples_locked = samples_locked.union(samples_transit)
        msg_locked = msg_locked + ' | Shipment cannot be closed if status is not among delivered/undeliverd/cancelled! '

    nlocked = samples_locked.count()
    if nlocked > 0:
        samples_locked = samples_locked.distinct().all()
        ids_locked = [sample[0] for sample in samples_locked]
        sample_ids = [sample_id for sample_id in sample_ids if sample_id not in ids_locked]
        msg_locked = msg_locked + '=> %d samples (cant be added to cart): '%nlocked + ', '.join(["LIMBSMP-%s" % ids_locked])
    else:
        ids_locked = []
        msg_locked = ''

    if len(sample_ids) == 0:
        return locked_response(msg_locked)

    n_new = 0
    n_old = 0
    for sample_id in sample_ids:
        new_uc = UserCart.query.filter_by(
            author_id=tokenuser.id, sample_id=sample_id
        ).first()

        if new_uc is not None:
            new_uc.selected = True
            new_uc.updated_on = func.now()
            new_uc.editor_id = tokenuser.id
            n_old = n_old + 1
        else:
            new_uc = UserCart(
                sample_id=sample_id, selected=True, author_id=tokenuser.id
            )
            n_new = n_new + 1

        ets = (
            EntityToStorage.query.filter(
                EntityToStorage.sample_id == sample_id,
                EntityToStorage.rack_id is not None,
                EntityToStorage.removed is not True,
            )
            .order_by(EntityToStorage.entry_datetime.desc())
            .first()
        )
        if ets:
            new_uc.rack_id = ets.rack_id
            new_uc.storage_type = "RUC"
            rack = SampleRack.query.filter_by(id=ets.rack_id).first()
            if rack:
                rack.is_locked = True
                db.session.add(rack)

        try:
            db.session.add(new_uc)
            db.session.flush()
        except Exception as err:
            db.session.rollback()
            return transaction_error_response(err)

    msg = "%d samples added to Cart!" % n_new
    if (n_old > 0):
        msg = msg + " | " + "%d samples updated in Cart!" % n_old
    if len(msg_locked) > 0:
        msg = msg + " | " + "Locked/stored sample not added: %s" % msg_locked


    if shipment:
        shipment.is_locked = True
        shipment.update({"editor_id": tokenuser.id})
        msg = msg + ' | ' + "Shipment closed successfully!"

    try:
        db.session.add(shipment)
        db.session.commit()
        return success_with_content_message_response(shipment_uuid, message=msg)

    except Exception as err:
        db.session.rollback()
        return transaction_error_response(err)


@api.route("/cart/add/LIMBRACK-<id>", methods=["POST"])
@token_required
def add_rack_to_cart(id: int, tokenuser: UserAccount):
    rack_response = requests.get(
        url_for("api.storage_rack_view", id=id, _external=True),
        headers=get_internal_api_header(tokenuser),
    )

    if rack_response.status_code == 200:
        rackRecord = SampleRack.query.filter_by(id=id).first()
        if not rackRecord:
            return not_found("LIMBRACK-%s" % id)

        if rackRecord.is_locked:
            return locked_response("LIMBRACK-%s" % id)
        rackRecord.is_locked = True

        esCheck = EntityToStorage.query.filter_by(rack_id=id, shelf_id=None).all()
        if esCheck == []:
            return not_found("for the rack with sample(s)")

        ESRecords = EntityToStorage.query.filter_by(rack_id=id).all()
        for es in ESRecords:
            if es.sample_id is None and es.shelf_id is not None:
                db.session.delete(es)
                db.session.flush()
            elif es.sample_id is not None:
                try:
                    cart_sample_schema = new_cart_sample_schema.load(
                        {"sample_id": es.sample_id}
                    )
                except ValidationError as err:
                    return validation_error_response(err)

                check = UserCart.query.filter_by(
                    author_id=tokenuser.id, sample_id=es.sample_id
                ).first()

                if check != None:
                    return success_with_content_message_response({"rack_id": id}, "Sample already added to Cart")

                # es = EntityToStorage.query.filter_by(sample_id=es.sample_id).first()
                new_uc = UserCart(
                    sample_id=es.sample_id,
                    rack_id=id,
                    storage_type=CartSampleStorageType.RUC,
                    selected=True,
                    author_id=tokenuser.id,
                )
                db.session.add(new_uc)
                db.session.flush()
        try:
            db.session.commit()
            return success_with_content_message_response({"rack_id": id}, "Sample added to Cart")

        except Exception as err:
            db.session.rollback()
            return transaction_error_response(err)

    else:
        return rack_response.content


@api.route("/cart/select/shipment/LIMBSAMPLE-<sample_id>", methods=["POST"])
@token_required
def select_record_cart_shipment(sample_id: int, tokenuser: UserAccount):
    es_record = EntityToStorage.query.filter_by(sample_id=sample_id).first()
    if es_record is not None and es_record.rack_id is not None:
        sample_records = EntityToStorage.query.filter_by(
            rack_id=es_record.rack_id, shelf_id=None
        )
        for sample in sample_records:
            cart_response = requests.post(
                url_for(
                    "api.select_record_cart", sample_id=sample.sample_id, _external=True
                ),
                headers=get_internal_api_header(tokenuser),
            )
        return success_without_content_response()
    else:
        cart_response = requests.post(
            url_for("api.select_record_cart", sample_id=sample_id, _external=True),
            headers=get_internal_api_header(tokenuser),
        )
        return success_with_content_response(cart_response.status_code)


@api.route("/cart/select/LIMBSAMPLE-<sample_id>", methods=["POST"])
@token_required
def select_record_cart(sample_id: int, tokenuser: UserAccount):
    ucRecord = UserCart.query.filter_by(sample_id=sample_id).first()
    ucRecord.selected = True
    try:
        db.session.commit()
        return success_without_content_response()

    except Exception as err:
        return transaction_error_response(err)


@api.route("/cart/deselect/shipment/LIMBSAMPLE-<sample_id>", methods=["POST"])
@token_required
def deselect_record_cart_shipment(sample_id: int, tokenuser: UserAccount):
    es_record = EntityToStorage.query.filter_by(sample_id=sample_id).first()
    if es_record is not None and es_record.rack_id is not None:
        sample_records = EntityToStorage.query.filter_by(
            rack_id=es_record.rack_id, shelf_id=None
        )
        for sample in sample_records:
            if sample is not None:
                cart_response = requests.post(
                    url_for(
                        "api.deselect_record_cart",
                        sample_id=sample.sample_id,
                        _external=True,
                    ),
                    headers=get_internal_api_header(tokenuser),
                )
        return success_without_content_response()

    cart_response = requests.post(
        url_for("api.deselect_record_cart", sample_id=sample_id, _external=True),
        headers=get_internal_api_header(tokenuser),
    )
    return success_with_content_response(cart_response.status_code)


@api.route("/cart/deselect/LIMBSAMPLE-<sample_id>", methods=["POST"])
@token_required
def deselect_record_cart(sample_id: int, tokenuser: UserAccount):
    ucRecord = UserCart.query.filter_by(sample_id=sample_id).first()
    ucRecord.selected = False
    try:
        db.session.commit()
        return success_without_content_response()

    except Exception as err:
        return transaction_error_response(err)
