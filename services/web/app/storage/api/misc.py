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

from flask import request, current_app, jsonify, send_file
from sqlalchemy import func
from ...api import api
from ...api.responses import *
from ...api.filters import generate_base_query_filters, get_filters_and_joins
from ...sample.api.base import func_update_sample_status
from ...decorators import token_required
from ...webarg_parser import use_args, use_kwargs, parser
from ...database import *

from marshmallow import ValidationError

from ..views.misc import (
    tree_sites_schema,
    new_sample_to_sample_rack_schema,
    new_sample_to_shelf_schema,
    new_sample_rack_to_shelf_schema,
)

from ...sample.enums import CartSampleStorageType


@api.route("/storage/transfer/rack_to_shelf", methods=["POST"])
@token_required
def storage_transfer_rack_to_shelf(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        rack_to_shelf_result = new_sample_rack_to_shelf_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    ets = EntityToStorage.query.filter_by(
        rack_id=values["rack_id"], storage_type="BTS"
    ).first()

    if ets is not None:
        ets.box_id = None
        ets.shelf_id = values["shelf_id"]
        ets.editor_id = tokenuser.id
        ets.storage_type = "BTS"

    else:
        ets = EntityToStorage(**rack_to_shelf_result)
        ets.author_id = tokenuser.id
        ets.storage_type = "BTS"
        db.session.add(ets)

    try:
        db.session.commit()
        msg = "The rack successfully added to shelf! "
        return success_with_content_message_response(values, msg)
    except Exception as err:
        return transaction_error_response(err)


@api.route("/storage/transfer/racks_to_shelf", methods=["POST"])
@token_required
def storage_transfer_racks_to_shelf(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    rack_ids = values.pop("rack_id")
    if len(rack_ids) == 0:
        return no_values_response()

    for rack_id in rack_ids:
        rack_values = values
        rack_values["rack_id"] = rack_id

        try:
            rack_to_shelf_result = new_sample_rack_to_shelf_schema.load(rack_values)

        except ValidationError as err:
            return validation_error_response(err)

        # etss = EntityToStorage.query.filter_by(rack_id=values["rack_id"],
        #             storage_type='BTS', removed=True).all()
        # if len(etss)>0:
        #     try:
        #         for ets in etss:
        #             # ets.removed = True
        #             # ets.editor_id = tokenuser.id
        #             # ets.updated_on = func.now()
        #             # db.session.add(ets)
        #             db.session.delete(ets)
        #
        #         db.session.flush()
        #         print('okok')
        #     except Exception as err:
        #         return transaction_error_response(err)

        ets = EntityToStorage(**rack_to_shelf_result)
        ets.author_id = tokenuser.id
        ets.storage_type = "BTS"
        try:
            db.session.add(ets)
            db.session.flush()

        except Exception as err:
            return transaction_error_response(err)

        ucs = UserCart.query.filter_by(rack_id=rack_id, storage_type="RUC").all()

        try:
            for uc in ucs:
                db.session.delete(uc)
                db.session.flush()

        except Exception as err:
            return transaction_error_response(err)

    try:
        db.session.commit()
        msg = "Rack successful added to shelf! "
        # return success_with_content_response({"success": True})
    except Exception as err:
        return transaction_error_response(err)

    # -- Unlock the rack after it is stored.
    for rack_id in rack_ids:
        rk = SampleRack.query.filter_by(id=rack_id).first()
        if rk is None:
            return not_found("LIMBRACK-%s:%s" % rack_id + " | " + msg)

        if rk.is_locked:
            rk.is_locked = False
            rk.editor_id = tokenuser.id
            rk.updated_on = func.now()

            try:
                db.session.add(rk)
            except Exception as err:
                return transaction_error_response(err)

    # -- Update status for samples in the rack
    samples = (
        Sample.query.join(EntityToStorage)
        .filter(
            EntityToStorage.storage_type == "STB", EntityToStorage.rack_id.in_(rack_ids)
        )
        .all()
    )

    if len(samples) > 0:
        try:
            for sample in samples:
                sample_status_events = {"sample_storage": None}
                res = func_update_sample_status(
                    tokenuser=tokenuser,
                    auto_query=True,
                    sample=sample,
                    events=sample_status_events,
                )
                if res["sample"]:
                    db.session.add(res["sample"])

            msg_status = "Sample status updated! "
        except Exception:
            msg_status = "Errors in updating sample status!"

    try:
        db.session.commit()
        msg = msg + "Racks unlocked! " + msg_status

        return success_with_content_message_response(rack_ids, msg)
    except Exception as err:
        return transaction_error_response(err)


# deprecated, use storage_transfer_sampleS_to_shelf instead
@api.route("/storage/transfer/sample_to_shelf", methods=["POST"])
@token_required
def storage_transfer_sample_to_shelf(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    try:
        sample_to_shelf_result = new_sample_to_shelf_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    etss = EntityToStorage.query.filter(sample_id=values["sample_id"]).all()
    if len(etss) > 0:
        # warning, confirmation
        try:
            for ets in etss:
                db.session.delete(ets)
        except Exception as err:
            return transaction_error_response(err)

    #
    # etss = EntityToStorage.query.filter_by(sample_id=values["sample_id"], storage_type='STS').all()
    # if ets != None:
    #     ets.box_id = None
    #     ets.shelf_id = values["shelf_id"]
    #     ets.editor_id = tokenuser.id
    #     ets.updated_on = func.now()
    #     ets.storage_type = "STS"

    ets = EntityToStorage(
        sample_id=values["sample_id"],
        shelf_id=values["shelf_id"],
        storage_type="STS",
        entry=values["entry"],
        entry_datetime=values["entry_datetime"],
        author_id=tokenuser.id,
    )
    try:
        db.session.add(ets)
        db.session.flush()
    except Exception as err:
        return transaction_error_response(err)

    usercart = UserCart.query.filter_by(
        sample_id=values["sample_id"], author_id=tokenuser.id
    ).first()
    if usercart:
        try:
            db.session.delete(usercart)
        except Exception as err:
            return transaction_error_response(err)

    try:
        db.session.commit()
        return success_with_content_response({"success": True})
    except Exception as err:
        return transaction_error_response(err)


@api.route("/storage/transfer/samples_to_shelf", methods=["POST"])
@token_required
def storage_transfer_samples_to_shelf(tokenuser: UserAccount):
    values = request.get_json()

    if not values:
        return no_values_response()

    sample_ids = values.pop("sample_id")
    if not sample_ids or len(sample_ids) == 0:
        return not_found("sample")

    for sample_id in sample_ids:
        values["sample_id"] = sample_id

        try:
            sample_to_shelf_result = new_sample_to_shelf_schema.load(values)
        except ValidationError as err:
            return validation_error_response(err)

        # etss = EntityToStorage.query.filter_by(sample_id=values["sample_id"], storage_type='STB').all()
        etss = EntityToStorage.query.filter_by(sample_id=values["sample_id"]).all()
        # TODO: instead of deleting exisint etss add new ets instance and set the existing ets to: removed=True
        if len(etss) > 0:
            # warning, confirmation
            try:
                for ets in etss:
                    db.session.delete(ets)
            except Exception as err:
                return transaction_error_response(err)
        # ets = EntityToStorage.query.filter_by(sample_id=values["sample_id"], storage_type='STS').first()
        # if ets != None:
        #     ets.box_id = None
        #     ets.shelf_id = values["shelf_id"]
        #     ets.editor_id = tokenuser.id
        #     ets.updated_on = func.now()
        #     ets.storage_type = "STS"

        ets = EntityToStorage(
            sample_id=values["sample_id"],
            shelf_id=values["shelf_id"],
            storage_type="STS",
            entry=values["entry"],
            entry_datetime=values["entry_datetime"],
            author_id=tokenuser.id,
        )
        try:
            db.session.add(ets)
            db.session.flush()
        except Exception as err:
            return transaction_error_response(err)

        usercart = UserCart.query.filter_by(
            sample_id=values["sample_id"], author_id=tokenuser.id
        ).first()
        if usercart:
            try:
                db.session.delete(usercart)
            except Exception as err:
                return transaction_error_response(err)

    try:
        db.session.commit()
        msg = "Samples successfully stored to shelf"
        # return success_with_content_response({"success": True, "message": msg})
    except Exception as err:
        return transaction_error_response(err)

    # -- Update sample status
    samples = Sample.query.filter(Sample.id.in_(sample_ids)).all()
    if len(samples) > 0:
        try:
            for sample in samples:
                sample_status_events = {"sample_storage": None}
                res = func_update_sample_status(
                    tokenuser=tokenuser,
                    auto_query=True,
                    sample=sample,
                    events=sample_status_events,
                )

                if res["sample"]:
                    db.session.add(res["sample"])
            msg_status = "Sample status updated! "
        except:
            msg_status = "Errors in updating sample status!"

    try:
        db.session.commit()
    except:
        msg_status = "Errors in updating sample status!"
    msg = msg + msg_status
    return success_with_content_message_response(sample_ids, msg)


@api.route("/storage/tree", methods=["GET"])
@token_required
def storage_view_tree(tokenuser: UserAccount):

    return success_with_content_response(
        tree_sites_schema.dump(SiteInformation.query.all())
    )

def site_home_tokenuser(tokenuser: UserAccount):
    if tokenuser.is_admin:
        choices = [(None, "None")]
        sites = basic_sites_schema.dump(SiteInformation.query.all())
    else:
        choices = []
        sites = basic_sites_schema.dump(SiteInformation.query.filter_by(id=tokenuser.site_id).all())

    for site in sites:
        choices.append(
            (
                site["id"],
                "<%s>%s - %s" % (site["id"], site["name"], site["description"])
            )
        )

    return success_with_content_response({'site_info': sites, 'choices': choices, 'user_site_id': tokenuser.site_id})

@api.route("/storage/tree/tokenuser", methods=["GET"])
@token_required
def storage_view_tree_tokenuser(tokenuser: UserAccount):
    if tokenuser.is_admin:
        return success_with_content_response(
            tree_sites_schema.dump(SiteInformation.query.all())
        )
    else:
        return success_with_content_response(
            tree_sites_schema.dump(SiteInformation.query.filter_by(id=tokenuser.site_id).all())
        )


@api.route("/storage", methods=["GET"])
@token_required
def storage_view_panel(tokenuser: UserAccount):

    data = {
        "basic_statistics": {
            "site_count": SiteInformation.query.count(),
            "building_count": Building.query.count(),
            "room_count": Room.query.count(),
            "cold_storage_count": ColdStorage.query.count(),
        },
        "cold_storage_statistics": {
            "cold_storage_type": prepare_for_chart_js(
                [
                    (type.value, count)
                    for (type, count) in db.session.query(
                        ColdStorage.type, func.count(ColdStorage.type)
                    )
                    .group_by(ColdStorage.type)
                    .all()
                ]
            ),
            "cold_storage_temp": prepare_for_chart_js(
                [
                    (type.value, count)
                    for (type, count) in db.session.query(
                        ColdStorage.temp, func.count(ColdStorage.temp)
                    )
                    .group_by(ColdStorage.temp)
                    .all()
                ]
            ),
        },
    }

    return success_with_content_response(data)
