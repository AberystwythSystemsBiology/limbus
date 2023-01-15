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
from __future__ import print_function

from flask import request, current_app, jsonify, send_file, flash, url_for
from ...api import api
from ...misc import get_internal_api_header
from ...api.generics import generic_edit, generic_lock, generic_new
from ...api.responses import *
from ...sample.api.base import func_update_sample_status, func_shelf_location
from ...api.filters import generate_base_query_filters, get_filters_and_joins
from ...decorators import token_required
from ...webarg_parser import use_args, use_kwargs, parser

from ...database import (
    db,
    SampleRack,
    UserAccount,
    EntityToStorage,
    ColdStorageShelf,
    ColdStorage,
    Room,
    Building,
    SiteInformation,
    Sample,
    UserCart,
)

from ..enums import EntityToStorageType

from sqlalchemy.sql import insert, func
from sqlalchemy import or_, and_, not_, select, text
from sqlalchemy.orm import aliased
from marshmallow import ValidationError

from ..views.rack import *
from ..views import new_sample_rack_to_shelf_schema
from ...sample.views import sample_schema, edit_sample_schema

from itertools import product


@api.route("/storage/rack", methods=["GET"])
@token_required
def storage_rack_home(tokenuser: UserAccount):

    return success_with_content_response(
        basic_sample_racks_schema.dump(SampleRack.query.all())
    )


@api.route("/storage/rack_tokenuser", methods=["GET"])
@token_required
def storage_rack_home_tokenuser(tokenuser: UserAccount):
    if tokenuser.is_admin:
        stmt = SampleRack.query.filter_by(is_locked=False)
        stmt2 = (
            db.session.query(SampleRack)
            .join(UserCart, SampleRack.id == UserCart.rack_id)
            .filter(UserCart.storage_type == "RUC")
        )

        stmt = stmt.union(stmt2).distinct(SampleRack.id).all()
        return success_with_content_response(basic_sample_racks_schema.dump(stmt))

    sites = [tokenuser.site_id]
    try:
        if "view_only" in tokenuser.settings:
            choices0 = tokenuser.settings["view_only"]["site"]["choices"]
        else:
            choices0 = tokenuser.settings["data_entry"]["site"]["choices"]
        if len(choices0) > 0:
            sites = list(set([sites + choices0 + [None]]))
    except:
        pass

    # -- Union of three types of rack
    # -- Type 1: empty rack not stored to shelf and no sample attached
    # sql_text = text("SELECT SampleRack.* " \
    #            "FROM SampleRack " \
    #            "LEFT OUTER JOIN EntityToStorage " \
    #             "ON SampleRack.id = EntityToStorage.rack_id " \
    #             "AND EntityToStorage.storage_type = 'BTS' " \
    #             "LEFT OUTER JOIN Sample " \
    #             "ON (Sample.id = EntityToStorage.sample_id " \
    #            "AND SampleRack.id = EntityToStorage.rack_id " \
    #            "AND EntityToStorage.storage_type = 'STB') " \
    #            "WHERE EntityToStorage.shelf_id is NULL " \
    #            "AND Sample.id is NULL "
    #                 )
    ids_bts = (
        db.session.query(SampleRack.id)
        .join(
            EntityToStorage,
            and_(
                SampleRack.id == EntityToStorage.rack_id,
                EntityToStorage.storage_type == "BTS",
            ),
        )
        .all()
    )

    ids_stb = (
        db.session.query(SampleRack.id)
        .join(
            EntityToStorage,
            and_(
                SampleRack.id == EntityToStorage.rack_id,
                EntityToStorage.storage_type == "STB",
            ),
        )
        .all()
    )

    ids_bts = [d[0] for d in ids_bts]
    ids_stb = [d[0] for d in ids_stb]

    # -- Type 1: rack not stored to shelf and no sample attached
    stmt = (
        db.session.query(SampleRack)
        .filter(~SampleRack.id.in_(ids_bts))
        .filter(~SampleRack.id.in_(ids_stb))
    )

    # -- Type 2: rack not stored to shelf but with associated samples with current_site_id in sites
    stmt = stmt.union(
        db.session.query(SampleRack)
        .join(
            EntityToStorage,
            and_(
                SampleRack.id == EntityToStorage.rack_id,
                EntityToStorage.storage_type == "STB",
                EntityToStorage.removed.is_(False),
            ),
        )
        .join(
            Sample,
            and_(
                Sample.id == EntityToStorage.sample_id,
                SampleRack.id == EntityToStorage.rack_id,
            ),
        )
        .filter(~SampleRack.id.in_(ids_bts))
        .filter(Sample.current_site_id.in_(sites))
    )

    # -- Type 3: racks stored on shelf in tokenuser's working sites
    stmt1 = (
        db.session.query(SampleRack)
        .join(
            EntityToStorage,
            and_(
                SampleRack.id == EntityToStorage.rack_id,
                EntityToStorage.storage_type == "BTS",
                EntityToStorage.removed.is_(False),
            ),
        )
        .join(ColdStorageShelf, EntityToStorage.shelf_id == ColdStorageShelf.id)
        .join(ColdStorage, ColdStorageShelf.storage_id == ColdStorage.id)
        .join(Room, ColdStorage.room_id == Room.id)
        .join(Building, Room.building_id == Building.id)
        .join(
            SiteInformation,
            and_(
                Building.site_id == SiteInformation.id,
                Building.site_id.in_(sites),
            ),
        )
    )

    # -- Finally racks in user cart
    stmt = (
        stmt.union(stmt1)
        .distinct(SampleRack.id)
        .filter(SampleRack.is_locked.is_(False))
    )

    stmt2 = (
        db.session.query(SampleRack)
        .join(UserCart, SampleRack.id == UserCart.rack_id)
        .filter(UserCart.author_id == tokenuser.id)
        .filter(UserCart.storage_type == "RUC")
    )

    stmt = stmt.union(stmt2).distinct(SampleRack.id).all()

    return success_with_content_response(basic_sample_racks_schema.dump(stmt))


@api.route("/storage/rack/LIMBRACK-<id>", methods=["GET"])
@token_required
def storage_rack_view(id, tokenuser: UserAccount):
    return success_with_content_response(
        rack_schema.dump(SampleRack.query.filter_by(id=id).first_or_404())
    )


@api.route("/storage/rack/new", methods=["POST"])
@token_required
def storage_rack_new(tokenuser: UserAccount):
    values = request.get_json()
    print("values", values)
    return generic_new(
        db,
        SampleRack,
        new_sample_rack_schema,
        basic_sample_rack_schema,
        values,
        tokenuser,
    )


@api.route("/storage/rack/new/with_samples", methods=["POST", "GET"])
@token_required
def storage_rack_new_with_samples(tokenuser: UserAccount):

    values = request.get_json()

    if not values:
        return no_values_response()

    if "samples" in values:
        samples_pos = values.pop("samples")
    else:
        samples_pos = values.pop("samples_pos")

    entry_datetime = values.pop("entry_datetime")
    entry = values.pop("entry")

    rack_values = values.pop("rack")
    # Step 1. Validate and add new sample rack
    try:
        result = new_sample_rack_schema.load(rack_values)
    except ValidationError as err:
        return validation_error_response(err)

    new_rack = SampleRack(**result)
    new_rack.author_id = tokenuser.id
    try:
        db.session.add(new_rack)
        db.session.flush()
        rack_id = new_rack.id
        print("new_rack id: ", rack_id)

    except Exception as err:
        return transaction_error_response(err)

    # Step 2. New entitytostorage with storage_type 'STB'
    for sample in samples_pos:
        sample["entry_datetime"] = entry_datetime
        sample["entry"] = entry

    # insert confirmed data to database
    return func_transfer_samples_to_rack(samples_pos, rack_id, tokenuser)


def func_transfer_samples_to_rack(samples_pos, rack_id, tokenuser: UserAccount):
    # Update entitytostorage with storage_type 'STB'
    for sample in samples_pos:
        # print("sample", sample)
        try:
            sample_id = sample["sample_id"]
        except:
            sample_id = sample["id"]

        # Step 1 Update existing entity to storage record for given sample
        #
        if sample_id:
            # record for sample to rack or sample to shelf given the sample id
            stbs = EntityToStorage.query.filter(
                EntityToStorage.sample_id == sample_id,
                EntityToStorage.storage_type != "BTS",
                # EntityToStorage.removed.is_(False),
            ).all()
            # record for existing sample to rack info given rack id
            stbs2 = EntityToStorage.query.filter(
                EntityToStorage.rack_id == rack_id,
                EntityToStorage.sample_id != sample_id,
                EntityToStorage.col == sample["col"],
                EntityToStorage.row == sample["row"],
                EntityToStorage.storage_type == "STB",
                # EntityToStorage.removed.is_(False),
            ).all()

        else:
            stbs = []
            # get storage record given the position of the sample on the rack
            stbs2 = EntityToStorage.query.filter(
                EntityToStorage.rack_id == rack_id,
                EntityToStorage.col == sample["col"],
                EntityToStorage.row == sample["row"],
                EntityToStorage.storage_type == "STB",
            ).all()

        if stbs2 is not None:
            # Remove the existing sample (of different sample_id) from current position of rack
            for stb in stbs2:
                try:
                    stb.removed = True
                    stb.update({"editor_id": tokenuser.id})
                    # db.session.delete(stb)
                    db.session.add(stb)

                except Exception as err:
                    return transaction_error_response(err)

        if len(stbs) > 0:  # is not None:
            for stb in stbs:

                try:
                    stb.col = sample["col"]
                    stb.row = sample["row"]
                    stb.storage_type = "STB"
                    stb.rack_id = rack_id
                    stb.shelf_id = None
                    stb.removed = False
                    if "entry_datetime" not in sample:
                        stb.entry_datetime = func.now()
                    else:
                        stb.entry_datetime = sample["entry_datetime"]

                    stb.update({"editor_id": tokenuser.id})
                    # db.session.delete(stb)
                    db.session.add(stb)

                except Exception as err:
                    print(err)
                    return transaction_error_response(err)

        if sample_id:
            if len(stbs) == 0:
                # Step 2. Add new sample to rack record
                # stb_values = {'sample_id': sample['sample_id'], 'row': sample['row'], 'col': sample['col'],
                #               'rack_id': rack_id, 'storage_type': 'STB'}

                stb_values = new_sample_to_sample_rack_schema.load(
                    sample, unknown="EXCLUDE"
                )

                new_stb = EntityToStorage(**stb_values)
                new_stb.storage_type = "STB"
                new_stb.author_id = tokenuser.id
                new_stb.removed = False
                new_stb.rack_id = rack_id
                if "entry_datetime" not in sample:
                    new_stb.entry_datetime = func.now()
                # if 'entry' not in sample:
                #     sample.entry = tokenuser.first_name[0]+tokenuser.last_name[0]

                try:
                    db.session.add(new_stb)
                except Exception as err:
                    print(err)
                    return transaction_error_response(err)

            if "changeset" in sample and len(sample["changeset"]) > 0:
                # -- Update sample info
                smpl = Sample.query.filter_by(id=sample_id).first()
                updset = {k: sample["changeset"][k][1] for k in sample["changeset"]}

                if smpl:
                    smpl.update(updset)
                    smpl.update({"editor_id": tokenuser.id})
                    try:
                        db.session.add(smpl)
                    except Exception as err:
                        return transaction_error_response(err)

            # Remove samples from usercart
            usercart = UserCart.query.filter_by(
                sample_id=sample_id, author_id=tokenuser.id
            ).first()
            # usercart = UserCart.query.filter_by(sample_id=sample_id).first()
            if usercart:
                try:
                    usercart.update({"editor_id": tokenuser.id})
                    db.session.delete(usercart)
                except Exception as err:
                    return transaction_error_response(err)

    try:
        # db.session.commit()
        db.session.flush()
        msg = "Sample(s) stored to rack Successfully! "
    except Exception as err:
        return transaction_error_response(err)

    # Update sample current_site_id/status
    sample_ids_not_updated = []
    for sample in samples_pos:
        sample_id = sample["sample_id"]
        if sample_id:
            res = func_update_sample_status(
                tokenuser=tokenuser,
                auto_query=True,
                sample_id=sample_id,
                events={"sample_storage": None},
            )

            # print("sample", sample, res["message"])
            if res["success"] is True and res["sample"]:
                try:
                    db.session.add(res["sample"])
                except:
                    sample_ids_not_updated.append(sample_id)
                    pass

    msg_status = ""
    if len(sample_ids_not_updated) > 0:
        msg_status = "%d samples not updated" % len(sample_ids_not_updated)

    try:
        db.session.commit()
        msg_status = "Sample status updated! " + msg_status
    except:
        msg_status = "Errors in updating sample status!"
        # return transaction_error_response(err)
    msg = msg + msg_status
    return success_with_content_message_response({"id": rack_id}, msg)


def func_rack_vacancies(num_rows, num_cols, occupancies=None):
    vacancies = [
        (i, j)
        for i, j in product(range(1, num_rows + 1), range(1, num_cols + 1))
        if (i, j) not in occupancies
    ]
    return vacancies


def func_rack_fill_with_samples(
    samples, num_rows, num_cols, vacancies, occupancies=None, fillopt=None
):
    if fillopt is None:
        fillopt = {"column_first": True, "num_channels": 0, "skip_gaps": True}

    print(fillopt)
    n_samples = len(samples)
    try:
        pos = [(samples[k]["row"], samples[k]["col"]) for k in range(n_samples)]
        return samples
    except:
        pass

    k = 0

    col_ini = 1
    row_ini = 1
    print("occupancies ", occupancies)
    if occupancies is not None and len(occupancies) > 0:
        if fillopt["skip_gaps"] is True:
            if fillopt["column_first"] is True:
                col_ids = [op[1] for op in occupancies]
                col_max = max(col_ids)
                row_ids = [op[0] for op in occupancies if op[1] == col_max]
                row_max = max(row_ids)

            else:
                row_ids = [op[0] for op in occupancies]
                row_max = max(row_ids)
                col_ids = [op[1] for op in occupancies if op[0] == row_max]
                col_max = max(col_ids)

            col_ini = col_max
            row_ini = row_max

    # print("col i: ", col_ini)
    # print("row i: ", row_ini)
    n_assigned = 0
    if fillopt["column_first"]:
        for col in range(col_ini, num_cols + 1):
            channel_cnt = 0
            if col == col_ini:
                col_pos = [(j, col) for j in range(row_ini, num_rows + 1)]
            else:
                col_pos = [(j, col) for j in range(1, num_rows + 1)]

            if fillopt["num_channels"] > 0:
                # If the row is not fully empty, skip this row
                if len(set(col_pos).intersect(set(vacancies))) > 0:
                    continue
            if col > col_ini:
                row_ini = 1
            for row in range(row_ini, num_rows + 1):
                if k == n_samples:
                    col = num_cols
                    break

                if (row, col) in vacancies:
                    samples[k].update({"row": row, "col": col, "pos": (row, col)})
                    k = k + 1
                    channel_cnt = channel_cnt + 1
                    if channel_cnt == fillopt["num_channels"]:
                        row = num_rows
                        # go for next row
                elif fillopt["num_channels"] > 0:
                    row = num_rows
                    # go for next row

    else:
        # ROW FIRST
        for row in range(row_ini, num_rows + 1):
            channel_cnt = 0
            if row == row_ini:
                row_pos = [(row, j) for j in range(num_cols + 1, col_ini)]
            else:
                row_pos = [(row, j) for j in range(1, num_cols + 1)]

            # row_pos = [(row, j) for j in range(1, num_cols + 1)]
            if fillopt["num_channels"] > 0:
                # If the row is not fully empty, skip this row
                if len(set(row_pos).intersect(set(vacancies))) > 0:
                    continue

            if row > row_ini:
                col_ini = 1
            for col in range(col_ini, num_cols + 1):
                if k == n_samples:
                    row = num_rows
                    break

                if (row, col) in vacancies:
                    sample_id = samples[k]["id"]
                    samples[k].update({"row": row, "col": col, "pos": (row, col)})
                    k = k + 1
                    channel_cnt = channel_cnt + 1
                    if channel_cnt == fillopt["num_channels"]:
                        col = num_cols  # go for next col

                elif fillopt["num_channels"] > 0:
                    col = num_cols  # go for next col

    return samples, k


def func_update_samples(samples, tokenuser):
    n_upd = 0
    for sample in samples:
        if "changeset" in sample and len(sample["changeset"]) > 0:
            # -- Update sample info
            sample_id = sample["id"]
            smpl = Sample.query.filter_by(id=sample_id).first()
            updset = {k: sample["changeset"][k][1] for k in sample["changeset"]}

            if smpl:
                smpl.update(updset)
                smpl.update({"editor_id": tokenuser.id})
                try:
                    db.session.add(smpl)
                    n_upd = n_upd + 1
                except Exception as err:
                    return transaction_error_response(err)

    try:
        db.session.commit()
        msg = "Info for %d sample(s) updated successfully! " % n_upd
        return {"success": True, "message": msg}
    except Exception as err:
        return transaction_error_response(err)


@api.route("/storage/rack/fill_with_samples", methods=["POST", "GET"])
@token_required
def storage_rack_fill_with_samples(tokenuser: UserAccount):
    samples = []
    if request.method == "POST":
        values = request.get_json()
        samples = values["samples"]

    else:
        values = None

    if len(samples) == 0:
        return no_values_response()

    entry_datetime = values.pop("entry_datetime", None)
    entry = values.pop("entry", None)

    rack_id = int(values["rack_id"])

    samples = values["samples"]
    # print("values: ", values)
    fillopt = {"column_first": True, "num_channels": 0, "skip_gaps": True}
    fillopt["column_first"] = values.pop("fillopt_column_first", True)
    fillopt["skip_gaps"] = values.pop("fillopt_skip_gaps", True)

    commit = False
    if "commit" in values and values["commit"]:
        commit = True

    # Step 1. Validate and add new sample rack
    rack = SampleRack.query.filter_by(id=rack_id).first()
    if rack is None:
        err = {"messages": "Rack not found!"}
        return validation_error_response(err)

    if not commit:
        stbs = EntityToStorage.query.filter(
            EntityToStorage.rack_id == rack_id,
            EntityToStorage.storage_type == "STB",
            EntityToStorage.removed.is_(False),
        ).all()

        occupancies = [(stb1.row, stb1.col) for stb1 in stbs]

        num_rows = rack.num_rows
        num_cols = rack.num_cols
        # Check if fully occupied
        vacancies = func_rack_vacancies(num_rows, num_cols, occupancies)
        if len(vacancies) < len(values["samples"]):
            err = {"messages": "Insufficient available positions in the selected rack!"}
            return validation_error_response(err)

        sample_ids = [sample["id"] for sample in samples]
        stbs = EntityToStorage.query.filter(
            EntityToStorage.sample_id.in_(sample_ids),
            EntityToStorage.storage_type == "STB",
            EntityToStorage.removed.is_(False),
        ).all()

        sample_ids_stored0 = [
            stb1.sample_id for stb1 in stbs if stb1.rack_id == rack_id
        ]
        sample_ids_stored1 = [
            stb1.sample_id for stb1 in stbs if stb1.rack_id != rack_id
        ]
        n_stored1 = len(sample_ids_stored1)
        # print('sample_ids_stored0 ', sample_ids_stored0)
        samples = [
            sample for sample in samples if sample["id"] not in sample_ids_stored0
        ]

        message = ""
        # print('n_stored1', n_stored1)
        if n_stored1 > 0:
            message = (
                "%d sample(s) already stored in a different rack, "
                "submit will change the location for these samples" % n_stored1
            )

        try:
            samples, n_assigned = func_rack_fill_with_samples(
                samples, num_rows, num_cols, vacancies, occupancies, fillopt
            )
            if n_assigned < len(samples):
                err = {
                    "messages": "Current fill option can assign only %d samples!"
                    % n_assigned
                }
                return validation_error_response(err)

        except:
            err = {"messages": "Errors in assigning a rack position to samples!"}
            return validation_error_response(err)

        samplestore = {"rack_id": rack_id, "samples": samples, "from_file": False}
        if entry_datetime:
            samplestore["entry_datetime"] = entry_datetime
            samplestore["entry"] = entry
        return success_with_content_message_response(samplestore, message)

    if entry_datetime:

        samples_pos = [
            {
                "sample_id": sample["id"],
                "row": sample["row"],
                "col": sample["col"],
                "entry_datetime": entry_datetime,
                "entry": entry,
            }
            for sample in samples
        ]
    else:
        samples_pos = [
            {"sample_id": sample["id"], "row": sample["row"], "col": sample["col"]}
            for sample in samples
        ]

    # insert confirmed data to database
    return func_transfer_samples_to_rack(samples_pos, rack_id, tokenuser)


@api.route("/storage/rack/edit_samples_pos", methods=["POST", "GET"])
@token_required
def storage_rack_edit_samples_pos(tokenuser: UserAccount):
    samples = []
    if request.method == "POST":
        values = request.get_json()
        samples = values["samples"]

    else:
        values = None

    if len(samples) == 0:
        return no_values_response()

    # entry_datetime = values.pop("entry_datetime", None)
    # entry = values.pop("entry", None)

    rack_id = int(values["rack_id"])
    samples = values["samples"]
    for sample in samples:
        stb = EntityToStorage.query.filter_by(
            sample_id=sample["id"], rack_id=rack_id, storage_type="STB", removed=False
        ).first()
        if stb:
            stb.update(
                {"row": sample["row"], "col": sample["col"], "editor_id": tokenuser.id}
            )
        else:
            return not_found("Relevant storage for sample: uuid=%s") % sample["uuid"]

        try:
            db.session.add(stb)
        except Exception as err:
            return transaction_error_response(err)

    try:
        db.session.commit()
        msg = "Sample positions in rack updated Successfully!"
        return success_with_content_message_response({"id": rack_id}, msg)
    except Exception as err:
        return transaction_error_response(err)


def func_dict_update(d0, d1, keys=[]):
    """Check the changeset when update d0 with d1
    Input:
        d0: original dictionary
        d1: dictionary containing updates
        keys - restricted the list of keys considered for update if not empty
    Return:
        [updated d0, dictionary of changes in tuple (pairs of values)]
    """
    changeset = {}
    du = d0.copy()
    du.update(d1)

    if len(keys) > 0:
        du = {k: du[k] for k in keys if k in du}

    for k in du:
        # print("du K", k, du[k], d0[k])
        if k not in d0:
            changeset[k] = (None, du[k])
        else:
            if du[k] != d0[k]:
                changeset[k] = (d0[k], du[k])

        d0[k] = du[k]

    d0["changeset"] = changeset
    return d0


def func_check_rack_samples(rack_id, samples):
    """
    Query existing sample info from database given the rack_id, and
    match the barcode provided based on sample position in the rack.
    Update 'changeset' in sample in case of any difference in the existing info

    Input
        rack_id: id for the rack where the sample info to be updated
        samples: list of samples with rack position (row, col) and barcode provided
    Return
        variables (in tuple)
            1. samples: list of samples with update info in changeset
            2. n_found: number of samples found in database
            3. err

    usage:
        samples, n_found, err = func_check_rack_samples(rack_id, samples)
    """
    n_found = 0
    err = None
    bcodes = []

    for sample in samples:
        if sample["barcode"] in [None, "", "empty", "EMPTY", "-"]:
            continue

        sample["id"] = None
        sample["sample_id"] = None

        smpl = (
            db.session.query(Sample)
            .join(EntityToStorage, Sample.id == EntityToStorage.sample_id)
            .filter(
                EntityToStorage.rack_id == rack_id,
                EntityToStorage.storage_type == "STB",
                EntityToStorage.removed.is_(False),
                EntityToStorage.row == sample["row"],
                EntityToStorage.col == sample["col"],
            )
            .first()
        )

        if smpl:
            sample0 = sample_schema.dump(smpl)
            sample0 = func_dict_update(sample0, sample, keys=["barcode"])
            if "barcode" in sample0["changeset"]:
                bcode1 = sample0["changeset"]["barcode"][1]
                if bcode1 in bcodes:
                    err = {
                        "messages": "Sample (%s) info error: duplicate barcode (%s) in the update file"
                        % (smpl.uuid, bcode1)
                    }
                    return samples, n_found, err

                bcodes.append(bcode1)
                bcode = (
                    db.session.query(Sample.barcode)
                    .filter(func.upper(Sample.barcode) == bcode1.upper())
                    .first()
                )
                if bcode is not None:
                    bcode = bcode[0]
                    err = {
                        "messages": "Sample (%s) info error: duplicate barcode (%s) in the database"
                        % (smpl.uuid, bcode)
                    }
                    return samples, n_found, err

            sample.update(sample0)
            sample["sample_id"] = smpl.id
            n_found = n_found + 1

    return samples, n_found, err


def func_get_samples(barcode_type, samples):
    """
    Query existing sample info from database and compare that with new info
    Update 'changeset' in sample in case of any difference in existing info
    Input
        barcode_type: column for identifying sample eg. uuid or barcode
        samples: list of samples with relevant info
    Return
        variables (in tuple)
            1. samples: list of samples with update info in changeset
            2. n_found: number of samples found in database
            3. err
    """
    n_found = 0
    err = None
    bcodes = []
    for sample in samples:
        filter = {barcode_type: sample["sample_code"]}
        sample["id"] = None
        sample["sample_id"] = None
        if sample["sample_code"] in [None, "", "empty", "EMPTY", "-"]:
            continue
        sample[barcode_type] = sample.pop("sample_code")
        smpl = db.session.query(Sample).filter_by(**filter).first()
        if smpl:
            # sample.update(sample_schema.dump(smpl))
            sample0 = sample_schema.dump(smpl)
            # sample0 = edit_sample_schema.dump(smpl)
            sample0 = func_dict_update(sample0, sample, keys=["barcode"])
            if "barcode" in sample0["changeset"]:
                bcode1 = sample0["changeset"]["barcode"][1]
                if bcode1 in bcodes:
                    err = {
                        "messages": "Sample (%s) info error: duplicate barcode (%s) in the update file"
                        % (smpl.uuid, bcode1)
                    }
                    return samples, n_found, err

                bcodes.append(bcode1)
                bcode = (
                    db.session.query(Sample.barcode)
                    .filter(func.upper(Sample.barcode) == bcode1.upper())
                    .first()
                )
                if bcode is not None:
                    bcode = bcode[0]
                    err = {
                        "messages": "Sample (%s) info error: duplicate barcode (%s) in the database"
                        % (smpl.uuid, bcode)
                    }
                    return samples, n_found, err

            # print("Upd sample: ", sample0["changeset"])
            sample.update(sample0)
            sample["sample_id"] = smpl.id
            n_found = n_found + 1

    return samples, n_found, err


@api.route("/storage/rack/refill_with_samples", methods=["POST", "GET"])
@token_required
def storage_rack_refill_with_samples(tokenuser: UserAccount):
    samples = []
    if request.method == "POST":
        values = request.get_json()
        if "samples" in values:
            samples = values["samples"]
    else:
        values = None

    if len(samples) == 0:
        return no_values_response()

    entry_datetime = values.pop("entry_datetime", None)
    entry = values.pop("entry", None)

    try:
        rack_id = int(values["rack_id"])
    except:
        rack_id = None

    if rack_id:
        # Step 1. Validate and add new sample rack
        rack = SampleRack.query.filter_by(id=rack_id).first()
        if rack is None:
            err = {"messages": "Rack not found!"}
            return validation_error_response(err)


    commit = False
    if "commit" in values and values["commit"]:
        commit = True
    else:
        samples, n_found, err = func_get_samples(values["barcode_type"], samples)
        # print("error", err)
        if err is not None:
            return validation_error_response(err)
        # print("samples_ids", samples)

    if not commit:

        sample_ids = [sample["id"] for sample in samples]
        stbs = EntityToStorage.query.filter(
            EntityToStorage.sample_id.in_(sample_ids),
            EntityToStorage.storage_type == "STB",
            EntityToStorage.removed.is_(False),
        ).all()

        sample_ids_stored1 = [
            stb1.sample_id for stb1 in stbs if stb1.rack_id != rack_id
        ]
        # n_stored0 = len(sample_ids_stored0)
        n_stored1 = len(sample_ids_stored1)
        # print('sample_ids_stored0 ', sample_ids_stored0)
        # samples = [sample for sample in samples if sample['id'] not in sample_ids_stored0]

        message = "%d samples found in the rack! " % n_found
        # print('n_stored1', n_stored1)
        if n_stored1 > 0:
            message = message + (
                "%d sample(s) already stored in a different rack, "
                "submit will change the location for these samples" % n_stored1
            )

        samplestore = {"rack_id": rack_id, "samples": samples, "from_file": True}
        # if entry_datetime:
        #     samplestore["entry_datetime"] = entry_datetime
        #     samplestore["entry"] = entry

        if "num_cols" in values:
            samplestore["num_cols"] = values["num_cols"]
        if "num_rows" in values:
            samplestore["num_rows"] = values["num_rows"]

        return success_with_content_message_response(samplestore, message)

    # samples_pos = samples
    # if entry_datetime:
    #     for sample in samples:
    #         if sample["id"]:
    #             sample.update({"entry_datetime": entry_datetime, "entry": entry})

    # insert confirmed data to database
    return func_transfer_samples_to_rack(samples, rack_id, tokenuser)


@api.route("/storage/rack/update_sample_barcode", methods=["POST", "GET"])
@token_required
def storage_rack_update_sample_barcode(tokenuser: UserAccount):
    # - Update barcode based on rack position
    samples = []
    if request.method == "POST":
        values = request.get_json()
        # print("valuesoooo", values)
        if "samples" in values:
            samples = values["samples"]
    else:
        values = None

    if len(samples) == 0:
        return no_values_response()

    # -- Get all samples in the rack
    try:
        rack_id = int(values["rack_id"])
    except:
        rack_id = None

    if rack_id:
        # Step 1. Validate and add new sample rack
        rack = SampleRack.query.filter_by(id=rack_id).first()
        if rack is None:
            err = {"messages": "Rack not found!"}
            return validation_error_response(err)

    commit = False
    if "commit" in values and values["commit"]:
        commit = True
    else:

        # -- Check changes in barcode, check duplication
        # print("ready!")
        print("rack_id! ", rack_id)
        samples, n_found, err = func_check_rack_samples(rack_id, samples)

        print("n_found", n_found)
        # print("error", err)
        if err is not None:
            return validation_error_response(err)

        if n_found < 1:
            return validation_error_response("No samples or barcode to update!")

    # -- Return info for update
    if not commit:
        message = "%d samples found in the rack to be updated! " % n_found
        samplestore = {
            "rack_id": rack_id,
            "samples": samples,
            "from_file": True,
            "update_storage": False,
        }

        if "num_cols" in values:
            samplestore["num_cols"] = values["num_cols"]
        if "num_rows" in values:
            samplestore["num_rows"] = values["num_rows"]

        return success_with_content_message_response(samplestore, message)

    # -- Update confirmed sample info (barcode only for the moment)
    return func_update_samples(samples, tokenuser)


@api.route("/storage/rack/LIMBRACK-<id>/query/rack", methods=["GET"])
@token_required
def storage_rack_to_shelf_check(id, tokenuser: UserAccount):
    uc = UserCart.query.filter_by(rack_id=id).first()
    if uc is not None:
        return success_with_content_response("RCT")
    ets = EntityToStorage.query.filter_by(
        rack_id=id, sample_id=None, removed=False
    ).first()
    if ets is not None:
        return success_with_content_response("RST")
    return success_with_content_response("RIV")


@api.route("/storage/query/SAMPLE-<id>", methods=["GET"])
@token_required
def storage_sample_to_entity_check(id, tokenuser: UserAccount):
    uc = UserCart.query.filter_by(sample_id=id).first()
    if uc is not None:
        return success_with_content_response("SCT")
    ets = EntityToStorage.query.filter_by(sample_id=id, removed=False).first()
    if ets is not None:
        return success_with_content_response("SRT")
    return success_with_content_response("SIV")


@api.route("/storage/rack/LIMBRACK-<id>/lock", methods=["POST"])
@token_required
def storage_rack_lock(id, tokenuser: UserAccount):
    return generic_lock(db, SampleRack, id, basic_sample_rack_schema, tokenuser)


@api.route("/storage/rack/LIMBRACK-<id>/edit", methods=["PUT"])
@token_required
def storage_rack_edit(id, tokenuser: UserAccount):
    # Step 1: SampleRack update
    # Step 2: If shelf_id exist, EntityToStorage update.
    values = request.get_json()
    print("values: ", values)
    if not values:
        return no_values_response()

    rack = SampleRack.query.get(id)

    if not rack:
        return not_found()

    storage_id = values["storage_id"]
    shelf_id = values["shelf_id"]
    values.pop("storage_id")
    values.pop("shelf_id")
    row = values.pop("compartment_row", None)
    col = values.pop("compartment_col", None)

    try:
        result = new_sample_rack_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    rack.update(values)
    rack.editor_id = tokenuser.id
    rack.updated_on = func.now()

    try:
        db.session.add(rack)
        db.session.commit()
        flash("Rack basic info edited!")
    except Exception as err:
        return transaction_error_response(err)

    stored = False
    if storage_id is not None and storage_id != "":
        storage = EntityToStorage.query.get(storage_id)
        if storage is not None:
            stored = True

    if stored:
        storage.shelf_id = shelf_id
        storage.row = row
        storage.col = col
        storage.editor_id = tokenuser.id
        storage.updated_on = func.now()

    else:
        # New EntityToStorage
        storage_values = {
            "shelf_id": shelf_id,
            "rack_id": rack.id,
            "row": row,
            "col": col,
            "storage_type": "BTS",
        }
        storage = EntityToStorage(**storage_values)
        storage.author_id = tokenuser.id
        # TODO: add entry date time and by to form
        storage.entry_datetime = func.now()

    try:
        db.session.add(storage)
        db.session.commit()
        flash("Rack storage shelf updated!")
        return success_with_content_response(values)
    except Exception as err:
        return transaction_error_response(err)


@api.route("/storage/rack/LIMBRACK-<id>/editbasic", methods=["PUT"])
@token_required
def storage_rack_edit_basic(id, tokenuser: UserAccount):
    values = request.get_json()
    return generic_edit(
        db, SampleRack, id, new_sample_rack_schema, rack_schema, values, tokenuser
    )


@api.route("/storage/RACK/LIMBRACK-<id>/delete", methods=["POST"])
@token_required
def storage_rack_delete(id, tokenuser: UserAccount):
    rackTableRecord = SampleRack.query.filter_by(id=id).first()

    if not rackTableRecord:
        return not_found()

    if rackTableRecord.is_locked:
        return locked_response()

    # Check samples stored in the rack
    entityStorageTableRecord = EntityToStorage.query.filter(
        EntityToStorage.rack_id == id
    ).all()

    shelfID = None
    for ets in entityStorageTableRecord:
        print(ets.storage_type)
        if ets.storage_type == EntityToStorageType.STB and ets.removed is False:
            return validation_error_response("Can't delete rack with assigned samples")

        elif ets.storage_type == EntityToStorageType.BTS and ets.removed is False:
            shelfID = ets.shelf_id
            ets.update({"editor_id": tokenuser.id})
            db.session.delete(ets)
            # return validation_error_response("Can't delete rack stored in a shelf %s" % shelfID)
        else:
            # Disassociate the other entitytostorage record with rack to deleted
            ets.rack_id = None
            ets.update({"editor_id": tokenuser.id})
            db.session.add(ets)

    try:
        db.session.flush()

        rackTableRecord.update({"editor_id": tokenuser.id})
        db.session.delete(rackTableRecord)
        db.session.commit()
        return success_with_content_response(shelfID)
    except Exception as err:
        return transaction_error_response(err)


@api.route("/storage/rack/location/LIMBRACK-<id>", methods=["GET"])
@token_required
def storage_rack_location(id, tokenuser: UserAccount):
    # Get shelf_id for the give rack id
    stmt = (
        db.session.query(SampleRack)
        .filter(SampleRack.id == id)
        .with_entities(
            SampleRack.id,
            SampleRack.serial_number,
            SampleRack.description,
            SampleRack.uuid,
        )
    )

    if stmt.count() > 0:
        result = [
            {
                "id": rackid,
                "serial_number": serial_number,
                "description": description,
                "uuid": uuid,
                "storage_id": None,
                "shelf_id": None,
                "compartment_row": None,
                "compartment_col": None,
            }
            for (rackid, serial_number, description, uuid) in [stmt.first()]
        ][0]

        stmt1 = (
            db.session.query(SampleRack)
            .join(EntityToStorage, SampleRack.id == EntityToStorage.rack_id)
            .join(
                ColdStorageShelf,
                and_(
                    EntityToStorage.shelf_id == ColdStorageShelf.id,
                    EntityToStorage.storage_type == "BTS",
                ),
            )
            .filter(
                SampleRack.id == id,
                EntityToStorage.removed.is_(False),
            )
            .with_entities(
                EntityToStorage.id,
                EntityToStorage.shelf_id,
                EntityToStorage.row,
                EntityToStorage.col,
            )
        )

        if stmt1.count() > 0:
            result1 = [
                {
                    "storage_id": storage_id,
                    "shelf_id": shelf_id,
                    "compartment_row": row,
                    "compartment_col": col,
                }
                for (storage_id, shelf_id, row, col) in [stmt1.first()]
            ][0]
            result.update(result1)

    return success_with_content_response(result)


def func_rack_storage_location(rack_id):
    stored_flag = False
    rack_storage = (
        EntityToStorage.query.filter(
            EntityToStorage.rack_id == rack_id,
            EntityToStorage.removed.is_(False),
            ~EntityToStorage.shelf_id.is_(None),
            EntityToStorage.storage_type == "BTS",
        )
        .order_by(EntityToStorage.entry_datetime.desc())
        .first()
    )

    rack_storage_info = None
    msg = "No rack storage info! "
    if rack_storage:
        shelf_id = rack_storage.shelf_id

        if shelf_id is None:
            shelf_storage = (
                EntityToStorage.query.filter(
                    EntityToStorage.rack_id == rack_storage.rack_id,
                    ~EntityToStorage.shelf_id.is_(None),
                    EntityToStorage.removed.is_(False),
                )
                .order_by(EntityToStorage.entry_datetime.desc())
                .first()
            )
            if shelf_storage:
                shelf_id = shelf_storage.shelf_id

                sample_storage_info = new_sample_rack_to_shelf_schema.dump(
                    shelf_storage
                )
                sample_storage_info["shelf_id"] = shelf_id
        else:
            sample_storage_info = new_sample_rack_to_shelf_schema.dump(shelf_storage)
            sample_storage_info["shelf_id"] = shelf_id

        msg = "No sample storage location info! "
        if shelf_id:
            shelf_loc = func_shelf_location(shelf_id)
            if shelf_loc["location"] is not None:
                sample_storage_info.update(shelf_loc["location"])
                msg = "Sample stored in %s! " % shelf_loc["pretty"]

        return {"sample_storage_info": sample_storage_info, "message": msg}


@api.route("/storage/rack/shelves_tokenuser/LIMBRACK-<id>", methods=["GET"])
@token_required
def storage_shelves_tokenuser(id, tokenuser: UserAccount):
    pass


@api.route("/storage/rack/shelves_onsite/LIMBRACK-<id>", methods=["GET"])
@token_required
def storage_shelves_onsite(id, tokenuser: UserAccount):
    # Get the list of shelves (excluding locked ones) of the same site for a given rack id
    # if rack id is None, then list the shelves from the same site of the user site

    if id is not None:
        subq = (
            db.session.query(SiteInformation.id)
            .join(Building)
            .join(Room)
            .join(ColdStorage)
            .join(ColdStorageShelf)
            .join(EntityToStorage, EntityToStorage.shelf_id == ColdStorageShelf.id)
            .filter(
                EntityToStorage.rack_id == id, EntityToStorage.storage_type == "BTS"
            )
        )

        stored = subq.count() > 0
        if stored:
            stmt = (
                db.session.query(SiteInformation.id)
                .join(Building)
                .join(Room)
                .join(ColdStorage)
                .join(ColdStorageShelf)
                .filter(
                    SiteInformation.id == subq.first().id, ~ColdStorageShelf.is_locked
                )
                .with_entities(
                    ColdStorageShelf.id,
                    SiteInformation.name,
                    Building.name,
                    Room.name,
                    ColdStorage.alias,
                    ColdStorage.temp,
                    ColdStorageShelf.name,
                )
                .distinct(ColdStorageShelf.id)
                .all()
            )

    if id is None or not stored:
        stmt = (
            db.session.query(SiteInformation.id)
            .join(Building)
            .join(Room)
            .join(ColdStorage)
            .join(ColdStorageShelf)
            .filter(
                or_(
                    SiteInformation.id == tokenuser.site_id, tokenuser.site_id.is_(None)
                ),
                ~ColdStorageShelf.is_locked,
            )
            .with_entities(
                ColdStorageShelf.id,
                SiteInformation.name,
                Building.name,
                Room.name,
                ColdStorage.alias,
                ColdStorage.temp,
                ColdStorageShelf.name,
            )
            .distinct(ColdStorageShelf.id)
            .all()
        )

    results = [
        {
            "id": shelfid,
            "name": "%s - %s - %s - %s (%s) - %s"
            % (sitename, buildingname, roomname, csname, cstemp, shelfname),
        }
        for (
            shelfid,
            sitename,
            buildingname,
            roomname,
            csname,
            cstemp,
            shelfname,
        ) in stmt
    ]

    return success_with_content_response(results)


@api.route("/storage/rack/info", methods=["GET"])
@token_required
def storage_rack_info(tokenuser: UserAccount):
    # Get the list of racks of the same site for a given user id
    # Not in use, replaced by storage_rack_home_tokenuser
    stmt = (
        db.session.query(SampleRack)
        .outerjoin(
            EntityToStorage,
            and_(
                SampleRack.id == EntityToStorage.rack_id,
                EntityToStorage.storage_type == "BTS",
            ),
        )
        .outerjoin(ColdStorageShelf, EntityToStorage.shelf_id == ColdStorageShelf.id)
        .outerjoin(ColdStorage, ColdStorageShelf.storage_id == ColdStorage.id)
        .outerjoin(Room, ColdStorage.room_id == Room.id)
        .outerjoin(Building, Room.building_id == Building.id)
        .outerjoin(
            SiteInformation,
            and_(
                Building.site_id == SiteInformation.id,
                Building.site_id == tokenuser.site_id,
            ),
        )
        .filter(~SampleRack.is_locked)
        .with_entities(
            SampleRack.id,
            SampleRack.num_rows,
            SampleRack.num_cols,
            SampleRack.serial_number,
            SampleRack.description,
            ColdStorageShelf.id,
            SiteInformation.name,
            Building.name,
            Room.name,
            ColdStorage.alias,
            ColdStorage.temp,
            ColdStorageShelf.name,
        )
        .distinct(SampleRack.id)
        .all()
    )

    results = [
        {
            "id": rackid,
            "num_rows": num_rows,
            "num_cols": num_cols,
            "serial_number": serial_number,
            "description": description or "",
            "location": "%s - %s - %s - %s (%s) - %s"
            % (
                sitename or "",
                buildingname or "",
                roomname or "",
                csname or "",
                cstemp or "",
                shelfname or "",
            ),
        }
        for (
            rackid,
            num_rows,
            num_cols,
            serial_number,
            description,
            shelfid,
            sitename,
            buildingname,
            roomname,
            csname,
            cstemp,
            shelfname,
        ) in stmt
    ]

    return success_with_content_response(results)


@api.route("/storage/rack/assign/sample", methods=["POST"])
@token_required
def storage_transfer_sample_to_rack(tokenuser: UserAccount):
    values = request.get_json()
    # print('values:', values)
    rack_id = int(values["rack_id"])
    if not values:
        return no_values_response()

    try:
        result = new_sample_to_sample_rack_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    # check if Sample exists.
    # ets = EntityToStorage.query.filter_by(sample_id=values["sample_id"]).first()
    etss = (
        EntityToStorage.query.filter_by(sample_id=values["sample_id"])
        .order_by(EntityToStorage.removed.asc())
        .all()
    )

    if len(etss) > 0:
        n = 0
        for ets in etss:
            n = n + 1
            if n > 1:
                ets.update({"editor_id": tokenuser.id})
                db.session.delete(ets)
                continue
            else:
                ets.shelf_id = None
                ets.rack_id = None
                ets.storage_type = "STB"
                ets.update(values)
                ets.removed = False
                ets.update({"editor_id": tokenuser.id})
                db.session.add(ets)
    else:
        ets = EntityToStorage(**values)
        ets.author_id = tokenuser.id
        ets.storage_type = "STB"
        ets.removed = False
        db.session.add(ets)

    try:
        db.session.flush()
    except Exception as err:
        db.session.rollback()
        return transaction_error_response(err)

    usercart = UserCart.query.filter_by(
        sample_id=values["sample_id"], author_id=tokenuser.id
    ).first()
    if usercart:
        try:
            db.session.delete(usercart)
        except:  # Exception as err:
            pass

    try:
        db.session.commit()
        msg = "Sample successfully assigned to rack! "
        # return success_with_content_response(view_sample_to_sample_rack_schema.dump(ets))
    except Exception as err:
        # print(">>>>>>>>>>>>>>>", err)
        db.session.rollback()
        return transaction_error_response(err)

    # ---- Update sample current_site_id/status
    res = func_update_sample_status(
        tokenuser=tokenuser,
        auto_query=True,
        sample_id=values["sample_id"],
        events={"sample_storage": None},
    )

    if res["success"] is True and res["sample"]:
        try:
            db.session.add(res["sample"])
            db.session.commit()
            msg_status = "Sample status updated! "
        except:
            msg_status = "Error in status update!! "

        msg = msg + msg_status

    return success_with_content_message_response({"id": rack_id}, msg)
