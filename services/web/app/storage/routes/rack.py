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

from flask import (
    redirect,
    abort,
    render_template,
    url_for,
    session,
    request,
    jsonify,
    Response,
    flash,
    current_app,
)
from flask_login import current_user, login_required

from .. import storage

from string import ascii_uppercase
import itertools
import re, csv, os
from datetime import datetime
import requests
from ...misc import get_internal_api_header
from uuid import uuid4
from ...decorators import check_if_admin

from ..forms import (
    NewSampleRackForm,
    EditSampleRackForm,
    SampleToEntityForm,
    SamplesToEntityForm,
    NewCryovialBoxFileUploadForm,
    CryoBoxFileUploadSelectForm,
    UpdateRackFileUploadForm,
    UpdateRackSampleInfoFileUploadForm,
)
from datetime import datetime
import tempfile

# def iter_all_strings():
#     for size in itertools.count(1):
#         for s in itertools.product(ascii_uppercase, repeat=size):
#             yield "".join(s)
#
#
# values = []
# for i in iter_all_strings():
#     values.append(i)
#     if i == "ZZZ":
#         break


@storage.route("/rack")
@login_required
def rack_index():
    response = requests.get(
        url_for("api.storage_rack_home", _external=True),
        headers=get_internal_api_header(),
    )

    if response.status_code == 200:
        return render_template(
            "storage/rack/index.html", racks=response.json()["content"]
        )

    return abort(response.status_code)


@storage.route("/rack/endpoint")
@login_required
def rack_endpoint():
    response = requests.get(
        url_for("api.storage_rack_home_tokenuser", _external=True),
        headers=get_internal_api_header(),
    )

    if response.status_code == 200:
        return response.json()
    return response.content


# @storage.route("/rack/endpoint_tokenuser")
# @login_required
# def rack_endpoint_tokenuser():
#     response = requests.get(
#         #url_for("api.storage_rack_info", _external=True),
#         url_for("api.storage_rack_home_toke", _external=True),
#         headers=get_internal_api_header(),
#     )
#
#     if response.status_code == 200:
#         return response.json()
#     return response.content


@storage.route("/rack/info")
@login_required
def rack_info():
    response = requests.get(
        url_for("api.storage_rack_info", _external=True),
        # url_for("api.storage_rack_home", _external=True),
        headers=get_internal_api_header(),
    )

    if response.status_code == 200:
        return response.json()
    return response.content


@storage.route("/rack/new", methods=["GET", "POST"])
@login_required
def add_rack():
    return render_template("storage/rack/new/option.html")


@storage.route("/rack/new/manual", methods=["GET", "POST"])
@login_required
def rack_manual_entry():
    form = NewSampleRackForm()
    if form.validate_on_submit():

        response = requests.post(
            url_for("api.storage_rack_new", _external=True),
            headers=get_internal_api_header(),
            json={
                "serial_number": form.serial.data,
                "num_rows": form.num_rows.data,
                "num_cols": form.num_cols.data,
                "colour": form.colours.data,
                "description": form.description.data,
            },
        )

        if response.status_code == 200:
            flash(
                "Sample Rack Added! Next: Assign the new rack to a cold storage shelf!!!"
            )
            # return redirect(url_for("storage.rack_index"))
            rack_id = response.json()["content"]["id"]
            return redirect(url_for("storage.edit_rack", id=rack_id))

    return render_template("storage/rack/new/manual/new.html", form=form)


def alpha2num(s):
    if s.isdigit():
        return s
    # Only the first letter will be used
    s = s.lower()
    num = 0
    for i in range(len(s)):
        num = num + (ord(s[-(i + 1)]) - 96) * (26 * i + 1)
    return num


def func_csvfile_to_json(csvfile, nrow=8, ncol=12) -> dict:
    data = {}
    csv_data = []

    expected_barcode = ["tube barcode", "barcode"]
    expected_uuid = ["identifier", "uuid"]
    expected_pos = ["tube position", "position", "pos"]
    expected_row = ["tube row", "row"]
    expected_col = ["tube column", "column", "col"]

    try:
        csvf = request.files[csvfile.name]
    except:
        try:
            csvf = request.files[csvfile]
        except:
            return {
                "success": False,
                "message": "File uploading error!",
            }

    csvpath = tempfile.NamedTemporaryFile(
        dir=os.path.join(current_app.config["TMP_DIRECTORY"]), delete=False
    )
    csvf.save(csvpath.name)

    header = None
    for code in ["utf-8", "unicode-escape"]:
        error = None
        try:
            print("code: ", code)
            with open(csvpath.name, newline="", encoding=code) as file:
                # print("dialect: ", csv.list_dialects())
                # dialect: ['excel', 'excel-tab', 'unix']
                dialect = csv.Sniffer().sniff(file.read())
                file.seek(0)
                try:
                    csv_file = csv.reader(file, dialect)
                    for row in csv_file:
                        # print("row", row)
                        if header is None:
                            header = row
                        else:
                            csv_data.append(row)
                except:
                    error = "csv"

            break

        except:
            error = "encode"
            continue

    if os.path.exists(csvpath.name):
        os.remove(csvpath.name)

    if error:
        if error == "encode":
            return {
                "success": False,
                "message": "File decoding error!",
            }

        if error == "csv":
            return {
                "success": False,
                "message": "File reading error! Make sure the file is in csv format!",
            }

    if len(csv_data) < 2:
        return {
            "success": False,
            "message": "File reading error! Check if the file format is comma separated, with headers",
        }

    header = [nm.lower().replace('"', "").replace("'", "") for nm in header]
    print("header", header)
    indexes = {}

    for key in expected_barcode:
        if key in header:
            indexes["barcode"] = header.index(key)

    for key in expected_uuid:
        if key in header:
            indexes["uuid"] = header.index(key)

    if "barcode" not in indexes and "uuid" not in indexes:
        return {
            "success": False,
            "message": "Missing column for sample code; "
            "should be one of the following in header (case insensitive): "
            "'Tube barcode', 'Barcode', 'identifier', 'uuid'",
        }

    for key in expected_pos:
        if key in header:
            indexes["position"] = header.index(key)

    if "position" not in indexes:
        for key in expected_row:
            if key in header:
                indexes["row"] = header.index(key)

        for key in expected_col:
            if key in header:
                indexes["col"] = header.index(key)

        if "row" not in indexes and "col" in indexes:
            return {
                "success": False,
                "message": "Missing column for tube row position; "
                "should be one of the following in header (case insensitive): "
                "'Tube Row', 'Row'",
            }

        if "col" not in indexes and "row" in indexes:
            return {
                "success": False,
                "message": "Missing column for tube col position; "
                "should be one of the following in header (case insensitive): "
                "'Tube Column', 'Col', 'Column'",
            }

        if "row" not in indexes and "col" not in indexes:
            return {
                "success": False,
                "message": "Missing column for tube position; "
                "should be one of the following in header (case insensitive): "
                "'Tube position', 'Position', 'Pos'",
            }

    code_types = [key for key in indexes]

    indexes.update({"rows": [], "columns": []})

    # print("codetype", code_types, indexes)

    if "position" in indexes:
        positions = {
            # -- note: to ignore the second code in the same field separated by space.
            x[indexes["position"]]: {
                ct: x[indexes[ct]].split(" ")[0] for ct in code_types
            }
            # x[indexes["position"]]: {ct: x[indexes[ct]] for ct in code_types}
            for x in csv_data[0:]
        }
        # print("positions", positions)

        data["positions"] = positions

        # Going to use plain old regex to do the splits
        regex = re.compile(r"(\d+|\s+)")

        for position in data["positions"].keys():
            splitted = regex.split(position)
            pos = []
            try:
                for s in splitted[0:2]:
                    # print("s: ", s)
                    if s.isdigit():
                        pos.append(int(s))
                    else:
                        pos.append(ord(s.lower()) - 96)

                indexes["rows"].append(pos[0])  # Letter e.g. A2: => Row 1
                indexes["columns"].append(pos[1])  # Number A2 => Column 2
            except:
                return {"success": False, "message": "Error in reading positions"}

    else:

        for x in csv_data[0:]:
            if not x[indexes["row"]].isalpha():
                return {"success": False, "message": "Tube row value not alphabet!!"}
            if not x[indexes["col"]].isdigit():
                return {"success": False, "message": "Tube column value not digit!!"}

        positions = {
            x[indexes["row"]]
            + x[indexes["col"]]: {ct: x[indexes[ct]].split(" ")[0] for ct in code_types}
            for x in csv_data[0:]
        }
        data["positions"] = positions

        for position in data["positions"]:
            dpos = data["positions"][position]
            # print("dpos: ", dpos)
            try:
                row_id = ord(dpos["row"].lower()) - 96
                col_id = int(dpos["col"])
                dpos["row"] = row_id
                dpos["col"] = col_id
                indexes["rows"].append(row_id)  # Letter e.g. A2: => Row 1
                indexes["columns"].append(col_id)  # Number A2 => Column 2
            except:
                return {"success": False, "message": "Error in reading positions"}

        # print("positions", positions)
        data["positions"] = positions

    if max(indexes["rows"]) > nrow or min(indexes["rows"]) < 1:
        return {"success": False, "message": "Position (row number) out of range!"}
    if max(indexes["columns"]) > ncol or min(indexes["columns"]) < 1:
        return {"success": False, "message": "Position (column number) out of range!"}

    data["num_rows"] = nrow  # max(indexes["row"])
    data["num_cols"] = ncol  # max(indexes["column"])
    data["code_types"] = code_types
    data["success"] = True
    return data


@storage.route("/rack/new/from_file", methods=["GET", "POST"])
@login_required
def rack_create_from_file():
    # ------
    # new the whole rack occupancy using csv file (often from the rack saner).
    # -----

    form = NewCryovialBoxFileUploadForm()

    if form.validate_on_submit():
        barcode_type = form.barcode_type.data
        err = None
        _samples = func_csvfile_to_json(
            form.file.data, form.num_rows.data, form.num_cols.data
        )

        if _samples["success"]:
            # print("barcode type", barcode_type, _samples["code_types"])
            if barcode_type not in _samples["code_types"]:
                err = (
                    "The provided sample code doesn't matched with the chosen type %s! "
                    % barcode_type
                )
        else:
            err = _samples["message"]

        if err:
            flash(err)
            return render_template(
                "storage/rack/new/from_file/step_one.html", form=form, session_data={}
            )

        samples = []
        for s in _samples["positions"].items():
            smpl = s[1]
            smpl.update(
                {
                    "sample_code": s[1][barcode_type],
                    "row": alpha2num(s[0][0]),
                    "col": int(s[0][1 : len(s[0])]),
                }
            )
            samples.append(smpl)

        rack_entry = {
            "serial_number": form.serial.data,
            "num_rows": form.num_rows.data,
            "num_cols": form.num_cols.data,
            "colour": form.colour.data,
            "description": form.description.data,
        }
        rack_data = {
            "rack_id": None,
            "barcode_type": form.barcode_type.data,
            "entry": form.entry.data,
            "entry_datetime": str(
                datetime.strptime(
                    "%s %s" % (form.entry_date.data, form.entry_time.data),
                    "%Y-%m-%d %H:%M:%S",
                )
            ),
            "samples": samples,
        }
        rack_data.update(rack_entry)

        rack_data["from_file"] = True
        sample_move_response = requests.post(
            url_for("api.storage_rack_refill_with_samples", _external=True),
            headers=get_internal_api_header(),
            json=rack_data,
        )

        if sample_move_response.status_code == 200:
            sampletostore = sample_move_response.json()["content"]
            sampletostore["new_rack"] = True
            sampletostore.update({"rack": rack_entry})

            return render_template(
                "storage/rack/view_sample_to_rack.html",
                id=id,
                sampletostore=sampletostore,
            )

        else:
            flash(sample_move_response.json()["message"])

    return render_template(
        "storage/rack/new/from_file/step_one.html", form=form, session_data={}
    )


@storage.route("/rack/query/rack", methods=["GET", "POST"])
def check_rack_to_shelf():
    data = {}
    data["id"] = request.json["id"]
    response = requests.get(
        url_for("api.storage_rack_to_shelf_check", id=int(data["id"]), _external=True),
        headers=get_internal_api_header(),
    )

    data["warning"] = response.json()["content"]

    return jsonify(data)


@storage.route("/rack/query/sample", methods=["GET", "POST"])
def check_sample_to_rack():
    data = {}
    data["id"] = request.json["id"]
    response = requests.get(
        url_for(
            "api.storage_sample_to_entity_check", id=int(data["id"]), _external=True
        ),
        headers=get_internal_api_header(),
    )

    data["warning"] = response.json()["content"]

    return jsonify(data)


@storage.route("/rack/LIMBRACK-<id>")
@login_required
def view_rack(id):
    response = requests.get(
        url_for("api.storage_rack_view", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    if response.status_code == 200:
        return render_template(
            "storage/rack/view.html", rack=response.json()["content"]
        )

    return abort(response.status_code)
    # return render_template("storage/rack/view.html", id=id)


@storage.route("/rack/LIMBRACK-<id>/endpoint")
@login_required
def view_rack_endpoint(id):
    def _assign_view(sample, rack_view):
        try:
            row, col = sample["row"], sample["col"]
            if sample["editor"] is None:
                sample["editor"] = sample["author"]

            rack_view["content"]["view"][row][col].update(sample)
            rack_view["content"]["view"][row][col].update(
                {
                    "empty": False,
                }
            )
            return 1, rack_view
        except Exception as e:
            pass
        return 0, rack_view

    view_response = requests.get(
        url_for("api.storage_rack_view", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    if view_response.status_code == 200:
        rack_view = view_response.json()

        _rack = []
        for row in range(
            rack_view["content"]["num_rows"] + 1
        ):  # row, col: index in array
            _rack.append({})
            for col in range(rack_view["content"]["num_cols"] + 1):
                _rack[row][col] = {"empty": True}  # row+1, col+1: position in the rack

        # - Initialise rack_view['view'] to 2d array with empty cells
        rack_view["content"]["view"] = _rack

        count = 0
        # - fill in the cells with samples
        for sample in rack_view["content"]["entity_to_storage_instances"]:
            add, rack_view = _assign_view(sample, rack_view)
            count += add

        # rack_view["content"].pop("entity_to_storage_instances")
        total = rack_view["content"]["num_cols"] * rack_view["content"]["num_rows"]
        rack_view["content"]["counts"] = {"full": count, "empty": total - count}

        return rack_view
    return abort(view_response.status_code)


@storage.route("/rack/LIMBRACK-<id>/assign/<row>/<column>", methods=["GET", "POST"])
@login_required
def assign_rack_sample(id, row, column):
    # ------
    # Select and store a single sample to a rack position from the selected samples in user's Sample Cart.
    # -----
    view_response = requests.get(
        url_for("api.storage_rack_view", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    if view_response.json()["content"]["is_locked"]:
        flash("The rack is locked!")
        return redirect(url_for("storage.view_rack", id=id))

    if view_response.json()["content"]["shelf"] is None:
        flash(
            "The rack has not been assigned to a shelf! Edit the rack location first!"
        )
        return redirect(url_for("storage.edit_rack", id=id))

    if view_response.status_code == 200:

        sample_response = requests.get(
            url_for("api.get_cart", _external=True),
            headers=get_internal_api_header(),
        )

        if sample_response.status_code == 200:
            samples = []
            for item in sample_response.json()["content"]:
                if item["selected"] and item["storage_type"] != "RUC":
                    samples.append(item["sample"])
            if len(samples) == 0:
                flash(
                    "Add samples to your sample cart and select from the cart first! "
                )
                return redirect(url_for("storage.view_rack", id=id))

            form = SampleToEntityForm(samples)

            if form.validate_on_submit():

                sample_move_response = requests.post(
                    url_for("api.storage_transfer_sample_to_rack", _external=True),
                    headers=get_internal_api_header(),
                    json={
                        "sample_id": form.samples.data,
                        "rack_id": id,
                        "row": row,
                        "col": column,
                        "entry_datetime": str(
                            datetime.strptime(
                                "%s %s" % (form.date.data, form.time.data),
                                "%Y-%m-%d %H:%M:%S",
                            )
                        ),
                        "entry": form.entered_by.data,
                    },
                )

                if sample_move_response.status_code == 200:
                    flash(sample_move_response.json()["message"])
                    return redirect(url_for("storage.view_rack", id=id))
                else:
                    flash(sample_move_response.json())

            return render_template(
                "storage/rack/sample_to_rack_pos.html",
                rack=view_response.json()["content"],
                row=row,
                column=column,
                form=form,
            )

    abort(view_response.status_code)


@storage.route("/rack/LIMBRACK-<id>/assign_samples_in_cart", methods=["GET", "POST"])
@login_required
def assign_rack_samples(id):
    # ------
    # Select and store sample(s) to a rack from the selected samples in user's Sample Cart.
    # -----

    view_response = requests.get(
        url_for("api.storage_rack_view", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    if view_response.json()["content"]["is_locked"]:
        flash("The rack is locked!")
        return redirect(url_for("storage.view_rack", id=id))

    if view_response.json()["content"]["shelf"] is None:
        flash(
            "The rack has not been assigned to a shelf! Edit the rack location first!"
        )
        return redirect(url_for("storage.edit_rack", id=id))

    if view_response.status_code == 200:

        sample_response = requests.get(
            url_for("api.get_cart", _external=True),
            headers=get_internal_api_header(),
        )

        if sample_response.status_code == 200:
            samples = []
            for item in sample_response.json()["content"]:
                if item["selected"] and item["storage_type"] != "RUC":
                    # samples.append({"id": item["sample"]["id"], "uuid": item["sample"]["uuid"]})
                    samples.append(item["sample"])

            if len(samples) == 0:
                flash("Add samples to your sample cart and select from the cart! ")
                return redirect(url_for("storage.view_rack", id=id))

            form = SamplesToEntityForm(samples)

            if form.validate_on_submit():
                sample_move_response = requests.post(
                    url_for("api.storage_rack_fill_with_samples", _external=True),
                    headers=get_internal_api_header(),
                    json={
                        "samples": [{"id": id1} for id1 in form.samples.data],
                        "rack_id": id,
                        "entry_datetime": str(
                            datetime.strptime(
                                "%s %s" % (form.date.data, form.time.data),
                                "%Y-%m-%d %H:%M:%S",
                            )
                        ),
                        "entry": form.entered_by.data,
                        "fillopt_column_first": form.fillopt_column_first.data,
                        "fillopt_skip_gaps": form.fillopt_skip_gaps.data,
                    },
                )

                if sample_move_response.status_code == 200:
                    sampletostore = sample_move_response.json()["content"]
                    for sample in sampletostore["samples"]:
                        for item in sample_response.json()["content"]:
                            if item["sample"]["id"] == sample["id"]:
                                sample.update(item["sample"])

                    return render_template(
                        "storage/rack/view_sample_to_rack.html",
                        id=id,
                        sampletostore=sampletostore,
                    )

                else:
                    flash(sample_move_response.json())
                    return redirect(url_for("storage.view_rack", id=id))

            return render_template(
                "storage/rack/sample_to_rack.html",
                rack=view_response.json()["content"],
                form=form,
            )

    return abort(view_response.status_code)


@storage.route(
    "/rack/LIMBRACK-<id>/auto_assign_sample_to_rack", methods=["GET", "POST"]
)
@login_required
def auto_assign_sample_to_rack(id):
    return render_template("storage/rack/view_sample_to_rack.html", id=id)


@storage.route("/rack/fill_with_samples", methods=["GET", "POST"])
@login_required
def storage_rack_fill_with_samples():
    if request.method == "POST":
        values = request.json
    else:
        return {"messages": "Sample and storage info needed!", "success": False}

    response = requests.post(
        url_for("api.storage_rack_fill_with_samples", _external=True),
        headers=get_internal_api_header(),
        json=values,
    )
    return response.json()


@storage.route("/rack/LIMBRACK-<id>/edit_samples_in_rack", methods=["GET", "POST"])
@login_required
def edit_rack_samples_pos(id):
    view_response = requests.get(
        url_for("api.storage_rack_view", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    if view_response.json()["content"]["is_locked"]:
        flash("The rack is locked!")
        return redirect(url_for("storage.view_rack", id=id))

    if view_response.json()["content"]["shelf"] is None:
        flash(
            "The rack has not been assigned to a shelf! Edit the rack location first!"
        )
        return redirect(url_for("storage.edit_rack", id=id))

    sampletostore = view_response.json()["content"]
    id = int(sampletostore.pop("id"))
    sampletostore = {
        "rack_id": id,
        "samples": [],
        "from_file": False,
        "update_only": True,
    }

    return render_template(
        "storage/rack/view_sample_to_rack.html", id=id, sampletostore=sampletostore
    )


@storage.route("/rack/edit_samples_pos", methods=["GET", "POST"])
@login_required
def storage_rack_edit_samples_pos():
    if request.method == "POST":
        values = request.json
    else:
        return {"messages": "Sample and storage info needed!", "success": False}

    response = requests.post(
        url_for("api.storage_rack_edit_samples_pos", _external=True),
        headers=get_internal_api_header(),
        json=values,
    )
    return response.json()


@storage.route("/rack/LIMBRACK-<id>/assign_samples_in_file", methods=["GET", "POST"])
@login_required
def update_rack_samples_from_file(id):
    # ------
    # Update the whole rack occupancy using csv file (often from the rack saner).
    # -----
    view_response = requests.get(
        url_for("api.storage_rack_view", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    if view_response.json()["content"]["is_locked"]:
        flash("The rack is locked!")
        return redirect(url_for("storage.view_rack", id=id))

    if view_response.json()["content"]["shelf"] is None:
        flash(
            "The rack has not been assigned to a shelf! Edit the rack location first!"
        )
        return redirect(url_for("storage.edit_rack", id=id))

    if view_response.status_code == 200:
        num_rows = view_response.json()["content"]["num_rows"]
        num_cols = view_response.json()["content"]["num_cols"]

        form = UpdateRackFileUploadForm()

        if form.validate_on_submit():
            barcode_type = form.barcode_type.data

            err = None

            _samples = func_csvfile_to_json(form.file.data, num_rows, num_cols)
            if _samples["success"]:
                print("barcode type", barcode_type, _samples["code_types"])
                if barcode_type not in _samples["code_types"]:
                    err = (
                        "The provided sample code doesn't matched with the chosen type %s! "
                        % barcode_type
                    )
            else:
                # err = "Errors in reading the file! "
                err = _samples["message"]

            if err:
                flash(err)
                return redirect(url_for("storage.view_rack", id=id))

            samples = []
            for s in _samples["positions"].items():
                # e.g. s=['B1', {'position': 'B1', 'barcode': '12345', 'uuid': 'edf77b31-ba28-4b3a-98d2-f9c058c3a865'}]
                smpl = s[1]
                smpl.update(
                    {
                        "sample_code": s[1][barcode_type],
                        "row": alpha2num(s[0][0]),
                        "col": int(s[0][1 : len(s[0])]),
                    }
                )
                samples.append(smpl)

            rack_data = {
                # "samples": [{"id": id1} for id1 in form.samples.data],
                "rack_id": id,
                "entry_datetime": str(
                    datetime.strptime(
                        "%s %s" % (form.entry_date.data, form.entry_time.data),
                        "%Y-%m-%d %H:%M:%S",
                    )
                ),
                "entry": form.entry.data,
                "barcode_type": form.barcode_type.data,
                "samples": samples,
            }

            sample_move_response = requests.post(
                url_for("api.storage_rack_refill_with_samples", _external=True),
                headers=get_internal_api_header(),
                json=rack_data,
            )

            if sample_move_response.status_code == 200:
                sampletostore = sample_move_response.json()["content"]

                return render_template(
                    "storage/rack/view_sample_to_rack.html",
                    id=id,
                    sampletostore=sampletostore,
                )

            else:
                flash(sample_move_response.json())
                return redirect(url_for("storage.view_rack", id=id))

        return render_template(
            "storage/rack/sample_to_rack_from_file.html",
            rack=view_response.json()["content"],
            form=form,
        )
    return abort(view_response.status_code)


@storage.route(
    "/rack/LIMBRACK-<id>/update_sample_info_in_file", methods=["GET", "POST"]
)
@login_required
def update_rack_sample_info_from_file(id):
    # ------
    # Update the whole rack occupancy using csv file (often from the rack saner).
    # -----
    view_response = requests.get(
        url_for("api.storage_rack_view", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    if view_response.json()["content"]["is_locked"]:
        flash("The rack is locked!")
        return redirect(url_for("storage.view_rack", id=id))

    if view_response.json()["content"]["shelf"] is None:
        flash(
            "The rack has not been assigned to a shelf! Edit the rack location first!"
        )
        return redirect(url_for("storage.edit_rack", id=id))

    if view_response.status_code == 200:
        num_rows = view_response.json()["content"]["num_rows"]
        num_cols = view_response.json()["content"]["num_cols"]

        form = UpdateRackSampleInfoFileUploadForm()

        if form.validate_on_submit():

            err = None

            _samples = func_csvfile_to_json(form.file.data, num_rows, num_cols)
            if _samples["success"]:
                barcode_type = "barcode"
                if barcode_type not in _samples["code_types"]:
                    err = "Missing barcode column! "
            else:
                # err = "Errors in reading the file! "
                err = _samples["message"]

            if err:
                flash(err)
                return redirect(url_for("storage.view_rack", id=id))

            samples = []
            for s in _samples["positions"].items():
                # e.g. s=['B1', {'position': 'B1', 'barcode': '12345', 'uuid': 'edf77b31-ba28-4b3a-98d2-f9c058c3a865'}]
                smpl = s[1]
                smpl.update(
                    {
                        "sample_code": s[1][barcode_type],
                        "row": alpha2num(s[0][0]),
                        "col": int(s[0][1 : len(s[0])]),
                    }
                )
                samples.append(smpl)

            rack_data = {
                "rack_id": id,
                "barcode_type": barcode_type,
                "samples": samples,
            }

            sample_update_response = requests.post(
                url_for("api.storage_rack_update_sample_barcode", _external=True),
                headers=get_internal_api_header(),
                json=rack_data,
            )

            if sample_update_response.status_code == 200:
                sampletostore = sample_update_response.json()["content"]

                return render_template(
                    "storage/rack/view_sample_to_rack.html",
                    id=id,
                    sampletostore=sampletostore,
                )

            else:

                flash(sample_update_response.json())
                return redirect(url_for("storage.view_rack", id=id))

        return render_template(
            "storage/rack/update_rack_sample_info_from_file.html",
            rack=view_response.json()["content"],
            form=form,
        )
    return abort(view_response.status_code)


@storage.route("/rack/new_with_samples", methods=["GET", "POST"])
@login_required
def storage_rack_create_with_samples():
    if request.method == "POST":
        values = request.json
    else:
        return {"messages": "Sample and storage info needed!", "success": False}

    response = requests.post(
        url_for("api.storage_rack_new_with_samples", _external=True),
        headers=get_internal_api_header(),
        json=values,
    )
    return response.json()


@storage.route("/rack/refill_with_samples", methods=["GET", "POST"])
@login_required
def storage_rack_refill_with_samples():
    if request.method == "POST":
        values = request.json
    else:
        return {"messages": "Sample and storage info needed!", "success": False}

    response = requests.post(
        url_for("api.storage_rack_refill_with_samples", _external=True),
        headers=get_internal_api_header(),
        json=values,
    )
    return response.json()


@storage.route("/rack/update_sample_info", methods=["GET", "POST"])
@login_required
def storage_rack_update_sample_info():
    if request.method == "POST":
        values = request.json
    else:
        return {"messages": "Sample and storage info needed!", "success": False}

    response = requests.post(
        url_for("api.storage_rack_update_sample_barcode", _external=True),
        headers=get_internal_api_header(),
        json=values,
    )
    return response.json()


@storage.route("rack/LIMBRACK-<id>/to_cart", methods=["GET", "POST"])
@login_required
def add_rack_to_cart(id):
    view_response = requests.get(
        url_for("api.storage_rack_view", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    if view_response.status_code == 200:
        to_cart_response = requests.post(
            url_for("api.add_rack_to_cart", id=id, _external=True),
            headers=get_internal_api_header(),
        )
        redirect(url_for("storage.view_rack", id=id))
        return to_cart_response.content
    return abort(view_response.status_code)


@storage.route("rack/LIMBRACK-<id>/edit", methods=["GET", "POST"])
@login_required
def edit_rack(id):
    response = requests.get(
        url_for("api.storage_rack_view", id=id, _external=True),
        headers=get_internal_api_header(),
    )
    if response.json()["content"]["is_locked"]:
        flash("The rack is locked!")
        return abort(401)

    if response.status_code == 200:
        response = requests.get(
            url_for("api.storage_rack_location", id=id, _external=True),
            # url_for("api.storage_rack_view", id=id, _external=True),
            headers=get_internal_api_header(),
        )

        sites_response = requests.get(
            url_for("api.site_home_tokenuser", _external=True),
            headers=get_internal_api_header(),
        )

        if sites_response.status_code == 200:
            sites = sites_response.json()["content"]["choices"]
            user_site_id = sites_response.json()["content"]["user_site_id"]

        # For SampleRack with location info.
        rack = response.json()["content"]
        # print("Rack: ", rack)
        shelves = []
        shelf_dict = {}
        shelf_required = True
        response1 = requests.get(
            url_for("api.storage_shelf_overview", _external=True),
            # url_for("api.storage_onsite_shelves", id=id, _external=True),
            headers=get_internal_api_header(),
        )

        if response1.status_code == 200:

            for site in sites:
                shelf_dict[site[0]] = []

            for shelf in response1.json()["content"]["shelf_info"]:
                if int(shelf["site_id"]) in shelf_dict:
                    shelf_dict[int(shelf["site_id"])].append(
                        [int(shelf["shelf_id"]), shelf["name"]]
                    )
                    shelves.append([int(shelf["shelf_id"]), shelf["name"]])

            # shelf_required = len(shelves) > 0

        print("rack: ", rack)
        form = EditSampleRackForm(
            sites=sites,
            shelves=shelves,
            data={
                "serial": rack["serial_number"],
                "description": rack["description"],
                "storage_id": rack["storage_id"],
                "shelf_id": rack["shelf_id"],
                "compartment_row": rack["compartment_row"],
                "compartment_col": rack["compartment_col"],
            },
        )

        delattr(form, "num_cols")
        delattr(form, "num_rows")
        delattr(form, "colours")
        # if not shelf_required:
        #    delattr(form, "shelf_id")

        if form.validate_on_submit():
            shelf_id = form.shelf_id.data
            if shelf_id == 0:
                shelf_id = None

            compartment_row = form.compartment_row.data
            compartment_col = form.compartment_col.data

            if compartment_row == 0:
                compartment_row = None
            if compartment_col == 0:
                compartment_col = None

            form_information = {
                "serial_number": form.serial.data,
                "description": form.description.data,
                "storage_id": form.storage_id.data,
                "shelf_id": shelf_id,
                "compartment_row": compartment_row,
                "compartment_col": compartment_col,
            }

            edit_response = requests.put(
                url_for("api.storage_rack_edit", id=id, _external=True),
                headers=get_internal_api_header(),
                json=form_information,
            )

            if edit_response.status_code == 200:
                flash("Rack Successfully Edited")
                return redirect(url_for("storage.view_rack", id=id))

            else:
                flash("We have a problem: %s" % (edit_response.json()["message"]))

        return render_template(
            "storage/rack/edit.html",
            form=form,
            rack=response.json()["content"],
            shelves=shelf_dict,
        )

    abort(response.status_code)


@storage.route("/rack/LIMBRACK-<id>/delete", methods=["GET", "POST"])
@login_required
def delete_rack(id):
    response = requests.get(
        url_for("api.storage_rack_view", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    if response.json()["content"]["is_locked"]:
        return abort(401)

    if response.status_code == 200:
        edit_response = requests.post(
            url_for("api.storage_rack_delete", id=id, _external=True),
            headers=get_internal_api_header(),
        )
        if edit_response.status_code == 200:
            flash("Rack Successfully Deleted")
            if edit_response.json()["content"] is None:
                return redirect(url_for("storage.rack_index"))
            return redirect(
                url_for(
                    "storage.view_shelf",
                    id=edit_response.json()["content"],
                    _external=True,
                )
            )

        else:
            flash("We have a problem. %s " % edit_response.json()["message"])

        return redirect(url_for("storage.view_rack", id=id, _external=True))

    abort(response.status_code)


@storage.route("/rack/LIMBRACK-<id>/lock", methods=["GET", "POST"])
@login_required
@check_if_admin
def lock_rack(id):

    response = requests.get(
        url_for("api.storage_rack_view", id=id, _external=True),
        headers=get_internal_api_header(),
    )
    if response.status_code == 200:
        edit_response = requests.post(
            url_for("api.storage_rack_lock", id=id, _external=True),
            headers=get_internal_api_header(),
        )

        if edit_response.status_code == 200:
            if edit_response.json()["content"]:
                flash("Rack Successfully Locked")
            else:
                flash("Rack Successfully Unlocked")
        else:
            flash("We have a problem: %s" % (edit_response.status_code))

        return redirect(url_for("storage.view_rack", id=id))

    return abort(response.status_code)
