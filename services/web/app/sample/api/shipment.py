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
from .base import func_update_sample_status, func_validate_settings

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
    SiteInformation,
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


@api.route("/cart/LIMBUSR-<user_id>", methods=["GET", "POST"])
@api.route("/user_cart", methods=["GET", "POST"])
@token_required
def get_user_cart(tokenuser: UserAccount, user_id=None):
    if user_id is None:
        user_id = tokenuser.id

    if not tokenuser.is_admin:
        if user_id != tokenuser.id:
            return validation_error_response("Permission denied!")

    cart = UserCart.query.filter_by(author_id=user_id).all()
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

        protocol_events = (
            db.session.query(SampleProtocolEvent)
            .join(SampleShipmentToSample)
            .filter(SampleShipmentToSample.shipment_id == shipment.id)
            .all()
        )

        # - Prior to delete protocol event, deassociate with event, which is used by sampleshipment
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

    # if shipped to external site, set status to delivered will close the shipment
    to_external = SiteInformation.query.filter_by(
        id=shipment.site_id, is_external=True
    ).first()
    if to_external:
        shipment.is_locked = True

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
    stmt = (
        SampleShipmentStatus.query.join(SampleShipment)
        .join(SampleShipmentToSample)
        .join(Sample)
        .filter(
            ~SampleShipmentToSample.id.is_(None),
            ~SampleShipmentToSample.sample_id.is_(None),
        )
    )
    print(stmt.count())
    if not tokenuser.is_admin:
        sites_tokenuser = func_validate_settings(
            tokenuser, keys={"site_id"}, check=False
        )
        sites_tokenuser = [None] + sites_tokenuser
        print("sites", sites_tokenuser)
        stmt = stmt.filter(
            Sample.status == "TRA", Sample.current_site_id.in_(sites_tokenuser)
        )

    shipments = stmt.all()
    return success_with_content_response(sample_shipments_status_schema.dump(shipments))


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

    for sample in cart:
        # -- check if it is of the same site
        if sample.sample.current_site_id == values["site_id"]:
            return validation_error_response(
                "Destination site same as the current site of sample (%s)! "
                % sample.sample.uuid
            )

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
        address_id=new_shipment_event_values["address_id"],
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
            protocol_event_id=new_protocol_event.id,
        )

        db.session.add(ssets)
        s.status = "TRA"
        # s.site_id = new_shipment_event.site_id
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
        # db.session.flush()

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
                db.update({"editor_id": tokenuser.id})
                db.session.delete(uc)
                db.session.flush()
        rackRecord = SampleRack.query.filter_by(id=id).first()
        rackRecord.is_locked = False
        try:
            db.session.commit()
        except Exception as err:
            return transaction_error_response(err)
        return success_with_content_message_response(
            {}, "All samples in rack %s removed from cart" % (id)
        )

    else:
        return success_with_content_response(rack_response.content)


# def func_validate_settings(tokenuser, keys={}, check=True):
#     success = True
#     msg = "Setting ok!"
#     sites_tokenuser = None
#     if "site_id" in keys:
#         if not tokenuser.is_admin:
#             sites_tokenuser = {tokenuser.site_id}
#             try:
#                 choices0 = tokenuser.settings["data_entry"]["site"]["choices"]
#                 if len(choices0) > 0:
#                     sites_tokenuser.update(set(choices0))
#             except:
#                 pass
#
#             sites_tokenuser = list(sites_tokenuser)
#             if check:
#                 if keys["site_id"] not in [None] + sites_tokenuser:
#                     success = False
#                     msg = "Data entry role required for handling the sample in its current site! "
#                     return sites_tokenuser, success, msg
#             else:
#                 return sites_tokenuser
#
#     if check:
#         return sites_tokenuser, success, msg
#     else:
#         return sites_tokenuser


def func_validate_samples_to_cart(
    tokenuser: UserAccount, sample_ids=[], to_close_shipment=False, rack_to_cart=False
):
    # -- Sample_locked: samples that could not be added to cart for storage/shipment
    # -- Sample_locked + Rack_locked + Sample_in_transit
    msg_locked = ""
    print("999", to_close_shipment, rack_to_cart)
    samples_locked = db.session.query(Sample.id).filter(
        Sample.id.in_(sample_ids), Sample.is_locked == True
    )

    n_locked = samples_locked.count()

    if n_locked > 0:
        msg_locked = msg_locked + " | %d Sample locked! " % n_locked

    if not tokenuser.is_admin:
        # -- Can only add samples of sites which the user have data entry permissions
        sites_tokenuser = func_validate_settings(
            tokenuser, keys={"site_id"}, check=False
        )

        samples_other = db.session.query(Sample.id).filter(
            Sample.id.in_(sample_ids),
            Sample.is_locked.is_(False),
            ~Sample.current_site_id.is_(None),
            ~Sample.current_site_id.in_(sites_tokenuser),
        )
        n_other = samples_other.count()
        if n_other > 0:
            samples_locked = samples_locked.union(samples_other)
            msg_locked = (
                msg_locked
                + "| Data entry role required for the associated site for %d samples!"
                % n_other
            )

    if to_close_shipment is False:
        # Locked samples union with samples with rack that have been locked
        samples_rack_locked = (
            db.session.query(Sample.id)
            .join(EntityToStorage, EntityToStorage.sample_id == Sample.id)
            .join(SampleRack, SampleRack.id == EntityToStorage.rack_id)
            .filter(Sample.id.in_(sample_ids), Sample.is_locked.is_(False))
            .filter(EntityToStorage.removed.is_(False))
            .filter(SampleRack.is_locked.is_(True))
        )
        print(samples_rack_locked)
        print("sample_ids", sample_ids)
        print("lock 11: ", samples_rack_locked.count())
        if rack_to_cart is True:
            samples_rack_incart = (
                db.session.query(UserCart.sample_id)
                .filter(UserCart.sample_id.in_(sample_ids))
                .filter(~UserCart.rack_id.is_(None))
                .filter(UserCart.storage_type == "RUC")
            )
            # Sample rack in user cart can be changed to different cart
            samples_rack_locked = samples_rack_locked.except_(samples_rack_incart)

        n_locked = samples_rack_locked.count()
        if n_locked > 0:
            msg_locked = msg_locked + " | %d samples (rack) locked/! " % n_locked

        # return False, msg_locked, sample_ids
        samples_locked = samples_locked.union(samples_rack_locked)
        # Samples in an open shipment can't be added to cart from sample view, but from shipment
        samples_transit = (
            db.session.query(Sample.id)
            .join(SampleShipmentToSample, SampleShipmentToSample.sample_id == Sample.id)
            .join(
                SampleShipment, SampleShipment.id == SampleShipmentToSample.shipment_id
            )
            .filter(
                Sample.id.in_(sample_ids),
                Sample.is_locked.is_(False),
                SampleShipment.is_locked.is_(False),
            )
        )

        n_transit = samples_transit.count()
        if n_transit > 0:
            samples_locked = samples_locked.union(samples_transit)
            msg_locked = msg_locked + " | %d samples in an open shipment! " % n_transit

    else:
        # -- to close a shipment
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
        if n_transit > 0:
            samples_locked = samples_locked.union(samples_transit)
            msg_locked = (
                msg_locked
                + " | Shipment cannot be closed if status is not among delivered/undeliverd/cancelled! "
            )

    n_locked = samples_locked.count()
    if n_locked > 0:
        samples_locked = samples_locked.distinct().all()
        ids_locked = [sample[0] for sample in samples_locked]
        sample_ids = [
            sample_id for sample_id in sample_ids if sample_id not in ids_locked
        ]
        msg_locked = (
            msg_locked
            + "=> In total: %d samples (cant be added to cart): " % n_locked
            + ", ".join(["LIMBSMP-%s" % ids_locked])
        )
    else:
        # ids_locked = []
        msg_locked = ""

    if len(sample_ids) == 0:
        return False, validation_error_response(msg_locked), sample_ids

    return True, msg_locked, sample_ids


def func_add_samples_to_cart(
    tokenuser: UserAccount, user_id=None, sample_ids=[],
    to_close_shipment=False, rack_to_cart=False,
    check=True
):

    if not user_id:
        user_id = tokenuser.id
        user = tokenuser

    if user_id != tokenuser.id:
        user = UserAccount.query.filter_by(id=user_id).first()
        if not user:
            return False, "User not found!"
    else:
        user = tokenuser

    if check:
        # success, msg_locked, sample_ids = func_validate_samples_to_cart(
        #     tokenuser, sample_ids, to_close_shipment, rack_to_cart
        # )
        success, msg_locked, sample_ids = func_validate_samples_to_cart(
            user, sample_ids, to_close_shipment, rack_to_cart
        )

        if not success:
            return False, msg_locked
    else:
        msg_locked = ""

    n_new = 0
    n_old = 0
    n_del = 0
    for sample_id in sample_ids:

        new_uc = UserCart.query.filter_by(
            author_id=user_id,
            sample_id=sample_id,
            editor_id=tokenuser.id
        ).first()

        if new_uc is not None:
            # -- Sample already added to the user cart
            new_uc.selected = True
            new_uc.update({"editor_id":tokenuser.id}) # update time
            n_old = n_old + 1
        else:
            # -- Remove sample from other user's cart
            new_ucs = UserCart.query\
                .filter_by(sample_id=sample_id)\
                .filter(UserCart.author_id!=user_id)\
                .all()

            for new_uc in new_ucs:
                n_del = n_del + 1
                new_uc.update({"editor_id": tokenuser.id})
                db.session.delete(new_uc)

            # -- Add to tokenuser's cart
            new_uc = UserCart(
                sample_id=sample_id, selected=True,
                author_id=user_id,
                editor_id=tokenuser.id
            )
            n_new = n_new + 1

        # -- keep only one entitytostorage record for each sample.
        # ets = (
        #     EntityToStorage.query.filter(
        #         EntityToStorage.sample_id == sample_id)
        #     .first()
        # )

        # -- dealing with legacy cases where we have multiple records for each sample
        etss = (
            EntityToStorage.query.filter(
                EntityToStorage.sample_id == sample_id)
            .order_by(EntityToStorage.removed.asc())
            .all()
            # EntityToStorage.removed.is_(False),
            #.order_by(EntityToStorage.entry_datetime.desc())
            #.first()
        )
        nd = 0
        for ets in etss:
            # -- only keep one record for sample
            nd = nd+1;
            if nd>1:
                ets.update({"editor_id": tokenuser.id})
                db.session.delete(ets)
                nd = nd+1
                continue

            if to_close_shipment is True or rack_to_cart is True:
                # - from transit to cart
                new_uc.rack_id = ets.rack_id
                new_uc.storage_type = "RUC"
                if rack_to_cart:
                    ets.shelf = None
                    ets.update({"editor_id": tokenuser.id})

                rack = SampleRack.query.filter_by(id=ets.rack_id).first()

                if rack:
                    rack.is_locked = True
                    rack.update({"editor_id": tokenuser.id})
                    db.session.add(rack)

            else:
                ets.update({"editor_id": tokenuser.id})
                ets.removed = True
                db.session.add(ets)
                # db.session.delete(ets)


        db.session.add(new_uc)

    try:
        db.session.flush()
    except Exception as err:
        db.session.rollback()
        return False, transaction_error_response(err)

    msg = "%d samples added to Cart!" % n_new
    if n_old > 0:
        msg = msg + " | " + "%d samples updated in Cart!" % n_old
    if n_del > 0:
        msg = msg + " | " + "%d samples deleted from Cart of other users!" % n_del

    # if msg_locked != "":
    #     msg = msg + " | " + "Locked/stored sample not added: %s" % msg_locked
    return True, msg


@api.route("/cart/add/<uuid>", methods=["POST"])
@token_required
def add_sample_to_cart(uuid: str, tokenuser: UserAccount):
    sample_id = db.session.query(Sample.id).filter_by(uuid=uuid).scalar()

    if not sample_id:
        return not_found("Sample %s" %uuid)

    sample_ids = [sample_id]

    success, msg = func_add_samples_to_cart(
        tokenuser=tokenuser, user_id=None,
        sample_ids=sample_ids, to_close_shipment=False,
        rack_to_cart=False, check=True
    )

    success=False
    if not success:
        return msg

    try:
        db.session.commit()
        return success_with_content_message_response(sample_ids, message=msg)

    except Exception as err:
        db.session.rollback()
        return transaction_error_response(err)



@api.route("/cart/add/samples", methods=["POST"])
@api.route("/cart/LIMBUSR-<user_id>/add/samples", methods=["POST"])
@token_required
def add_samples_to_cart(tokenuser: UserAccount, user_id=None):
    values = request.get_json()
    samples = []
    if values:
        samples = values.pop("samples", [])

    if len(samples) == 0:
        return no_values_response()

    sample_ids = [smpl["id"] for smpl in samples]

    success, msg = func_add_samples_to_cart(
        tokenuser, user_id, sample_ids,
        to_close_shipment=False, rack_to_cart=False, check=True
    )
    if not success:
        return msg

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
    shipment_id = values["id"]

    shipment = SampleShipment.query.filter_by(id=shipment_id).first()
    shipment_uuid = shipment.uuid
    if shipment.is_locked:
        return locked_response("Shipment uuid %s" % shipment_uuid)

    sample_ids = [smpl["sample_id"] for smpl in values["involved_samples"]]
    print("sample_ids", sample_ids)

    if len(sample_ids) == 0:
        return not_found("the involved samples for shipment uuid: %s" %shipment_uuid)

    success, msg = func_add_samples_to_cart(
        tokenuser, sample_ids, to_close_shipment=True
    )
    if not success:
        return msg

    if shipment:
        shipment.is_locked = True
        shipment.update({"editor_id": tokenuser.id})
        msg = msg + " | " + "Shipment closed successfully!"

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
    rackRecord = SampleRack.query.filter_by(id=id).first()
    if not rackRecord:
        return not_found("LIMBRACK-%s" % id)

    sample_ids = (
            db.session.query(EntityToStorage.sample_id)
            .filter_by(rack_id=id, storage_type="STB")
            .all()
    )

    if len(sample_ids) == 0:
        return not_found("for the rack with sample(s)")

    sample_ids = [smpl[0] for smpl in sample_ids]
    print("sample_ids", sample_ids)

    # -- Remove rack from shelf
    ESRecords = (EntityToStorage.query
                 .filter_by(rack_id=id, storage_type="BTS")
                 .order_by(EntityToStorage.removed)
                 .all())
    nd = 0
    for es in ESRecords:
        nd = nd+1
        if nd > 1:
            es.update({"editor_id": tokenuser.id})
            db.session.delete(es)
            continue

        if es.sample_id is None and es.shelf_id is not None:
            try:
                es.removed = True
                es.update({"editor_id": tokenuser.id})
                db.session.add(es)
                db.session.flush()
            except Exception as err:
                db.session.rollback()
                return transaction_error_response(err)

    success, msg = func_add_samples_to_cart(
        tokenuser, sample_ids, to_close_shipment=False, check=True, rack_to_cart=True
    )

    if not success:
        return validation_error_response(msg)

    try:
        db.session.commit()
        return success_with_content_message_response(id, message=msg)

    except Exception as err:
        db.session.rollback()
        return transaction_error_response(err)


#
# @api.route("/cart/add/LIMBRACK-<id>", methods=["POST"])
# @token_required
# def add_rack_to_cart(id: int, tokenuser: UserAccount):
#     rackRecord = SampleRack.query.filter_by(id=id).first()
#     if not rackRecord:
#         return not_found("LIMBRACK-%s" % id)
#
#     rackInCart = (
#         UserCart.query
#             .filter_by(rack_id=rackRecord.id, author_id=tokenuser.id)
#             .firt()
#     )
#     if rackInCart:
#         return validation_error_response("Rack already in the cart!")
#
#     racksInCart = (
#         UserCart.query.filter_by(rack_id=id)
#         .filter(UserCart.author_id!=tokenuser.id).all()
#     )
#
#     if rackRecord.is_locked and len(racksInCart) == 0:
#         return locked_response("LIMBRACK-%s" % id)
#
#     sample_ids = (
#         db.session.query(EntityToStorage.sample_id)
#         .filter_by(rack_id=id, storage_type="STB")
#         .all()
#     )
#
#     if len(sample_ids) == 0:
#         return not_found("for the rack with sample(s)")
#
#     sample_ids = [smpl[0] for smpl in sample_ids]
#     print("sample_ids", sample_ids)
#
#     success, msg_locked, sample_ids = func_validate_samples_to_cart(
#         tokenuser, sample_ids, to_close_shipment=False,
#     )
#     print(success, msg_locked, sample_ids)
#
#     if not success:
#         return msg_locked
#
#     rackRecord.is_locked = True
#
#     ESRecords = EntityToStorage.query.filter_by(rack_id=id).all()
#     for es in ESRecords:
#         if es.sample_id is None and es.shelf_id is not None:
#             try:
#                 db.session.delete(es)
#                 db.session.flush()
#             except Exception as err:
#                 db.session.rollback()
#                 return transaction_error_response(err)
#
#         elif es.sample_id is not None:
#
#             try:
#                 cart_sample_schema = new_cart_sample_schema.load(
#                     {"sample_id": es.sample_id}
#                 )
#             except ValidationError as err:
#                 return validation_error_response(err)
#
#             check = UserCart.query.filter_by(
#                 author_id=tokenuser.id, sample_id=es.sample_id
#             ).first()
#
#             if check != None:
#                 return success_with_content_message_response(
#                     {"rack_id": id}, "Sample already added to Cart"
#                 )
#
#             # es = EntityToStorage.query.filter_by(sample_id=es.sample_id).first()
#             new_uc = UserCart(
#                 sample_id=es.sample_id,
#                 rack_id=id,
#                 storage_type=CartSampleStorageType.RUC,
#                 selected=True,
#                 author_id=tokenuser.id,
#             )
#             db.session.add(new_uc)
#             db.session.flush()
#
#     try:
#         db.session.commit()
#         return success_with_content_message_response(
#             {"rack_id": id}, "Rack and associated samples added to Cart!"
#         )
#
#     except Exception as err:
#         db.session.rollback()
#         return transaction_error_response(err)
#


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
