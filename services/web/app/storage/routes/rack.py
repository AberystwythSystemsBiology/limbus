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
)
from flask_login import current_user, login_required

from .. import storage

from string import ascii_uppercase
import itertools
import re
from datetime import datetime
import requests
from ...misc import get_internal_api_header
from uuid import uuid4

from ..forms import (
    NewSampleRackForm, EditSampleRackForm,
    SampleToEntityForm,
    NewCryovialBoxFileUploadForm,
    CryoBoxFileUploadSelectForm,
)


def iter_all_strings():
    for size in itertools.count(1):
        for s in itertools.product(ascii_uppercase, repeat=size):
            yield "".join(s)


values = []
for i in iter_all_strings():
    values.append(i)
    if i == "ZZZ":
        break


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
            flash("Sample Rack Added")
            return redirect(url_for("storage.rack_index"))

    return render_template("storage/rack/new/manual/new.html", form=form)


@storage.route("rack/new/automatic", methods=["GET", "POST"])
@login_required
def rack_automatic_entry():
    def _file_to_json(data_stream) -> dict:
        data = {}
        csv_data = [x.decode("UTF-8").replace("\n", "").split(",") for x in data_stream]
        print(csv_data)
        indexes = {
            "Tube Barcode": csv_data[0].index("Tube Barcode"),
            "Tube Position": csv_data[0].index("Tube Position"),
            "Tube Row": [],
            "Tube Column": [],
        }

        positions = {
            x[indexes["Tube Position"]]: x[indexes["Tube Barcode"]]
            for x in csv_data[1:]
        }

        data["positions"] = positions

        # Going to use plain old regex to do the splits
        regex = re.compile(r"(\d+|\s+)")

        for position in data["positions"].keys():
            splitted = regex.split(position)
            indexes["Tube Column"].append(splitted[0])
            indexes["Tube Row"].append(int(splitted[1]))

        data["num_cols"] = len(list(set(indexes["Tube Column"])))
        data["num_rows"] = max(indexes["Tube Row"])

        return data

    form = NewCryovialBoxFileUploadForm()

    if form.validate_on_submit():
        _hash = str(uuid4())
        # replace with tempstore
        session[_hash] = {
            "serial_number": form.serial.data,
            "barcode_type": form.barcode_type.data,
            "serial_number": form.serial.data,
            "colour": form.colour.data,
            "description": form.description.data,
            "json": _file_to_json(form.file.data.stream),
        }
        return redirect(url_for("storage.rack_automatic_entry_validation", _hash=_hash))

    return render_template("storage/rack/new/from_file/step_one.html", form=form)


@storage.route("/rack/new/automatic/validation/<_hash>", methods=["GET", "POST"])
@login_required
def rack_automatic_entry_validation(_hash: str):
    session_data = session[_hash]
    sample_data = {}

    for position, identifier in session_data["json"]["positions"].items():
        sample = None
        if "identifier" != "":
            sample_response = requests.get(
                url_for("api.sample_query", _external=True),
                headers=get_internal_api_header(),
                json={session_data["barcode_type"]: identifier},
            )

            if sample_response.status_code == 200:
                sample = sample_response.json()["content"]
                sample_data[position] = sample

    form = CryoBoxFileUploadSelectForm(sample_data)

    if form.validate_on_submit():
        response = requests.post(
            url_for("api.storage_rack_new", _external=True),
            headers=get_internal_api_header(),
            json={
                "serial_number": session_data["serial_number"],
                "num_rows": session_data["json"]["num_rows"],
                "num_cols": session_data["json"]["num_cols"],
                "colour": session_data["colour"],
                "description": session_data["description"],
            },
        )

        if response.status_code == 200:

            _samples = []

            for element in form:
                if element.type == "BooleanField":
                    if element.data:
                        regex = re.compile(r"(\d+|\s+)")
                        col, row, _ = regex.split(element.id)
                        sample_id = element.render_kw["_sample"][0]["id"]
                        _samples.append([sample_id, values.index(col), row])

            responses = []

            for s in _samples:

                sample_move_response = requests.post(
                    url_for("api.storage_transfer_sample_to_rack", _external=True),
                    headers=get_internal_api_header(),
                    json={
                        "sample_id": s[0],
                        "rack_id": response.json()["content"]["id"],
                        "row": s[2],
                        "col": s[1],
                        "entry_datetime": str(datetime.now()),
                    },
                )

                responses.append([sample_move_response, s[0]])

            return redirect(
                url_for("storage.view_rack", id=response.json()["content"]["id"])
            )

        flash("We have an issue!")

    return render_template(
        "storage/rack/new/from_file/step_two.html",
        session_data=session_data,
        form=form,
        hash=_hash,
    )


@storage.route("/rack/LIMBRACK-<id>")
@login_required
def view_rack(id):
    return render_template("storage/rack/view.html", id=id)


@storage.route("/rack/LIMBRACK-<id>/endpoint")
@login_required
def view_rack_endpoint(id):
    def _assign_view(sample, rack_view):
        try:
            row, col = sample["row"], sample["col"]
            rack_view["content"]["view"][row]["%i\t%i" % (row, col)] = {
                "empty": False,
                "sample": sample["sample"],
            }
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

        for row in range(rack_view["content"]["num_rows"]):
            _rack.append({})
            for col in range(rack_view["content"]["num_cols"]):
                _rack[row]["%i\t%i" % (row, col)] = {"empty": True}

        rack_view["content"]["view"] = _rack

        count = 0

        for sample in rack_view["content"]["entity_to_storage_instances"]:
            add, rack_view = _assign_view(sample, rack_view)
            count += add

        total = rack_view["content"]["num_cols"] * rack_view["content"]["num_rows"]

        rack_view["content"]["counts"] = {"full": count, "empty": total - count}

        return rack_view
    return abort(view_response.status_code)


@storage.route("/rack/LIMBRACK-<id>/assign/<row>/<column>", methods=["GET", "POST"])
@login_required
def assign_rack_sample(id, row, column):
    view_response = requests.get(
        url_for("api.storage_rack_view", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    if view_response.status_code == 200:

        sample_response = requests.get(
            url_for("api.sample_home", _external=True),
            headers=get_internal_api_header(),
        )

        if sample_response.status_code == 200:

            form = SampleToEntityForm(sample_response.json()["content"])

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
                    return redirect(url_for("storage.view_rack", id=id))
                else:
                    flash(sample_move_response.json())

            return render_template(
                "storage/rack/sample_to_rack.html",
                rack=view_response.json()["content"],
                row=row,
                column=column,
                form=form,
            )

    abort(view_response.status_code)


@storage.route("rack/LIMBRACK-<id>/edit", methods=["GET", "POST"])
@login_required
def edit_rack(id):
    response = requests.get(
        url_for("api.storage_rack_location", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    if response.status_code == 200:
        # For SampleRack with location info.
        rack = response.json()["content"]
        #print("Rack: ", rack)
        shelves = []
        shelf_required = False

        if rack['storage_id']:
            response1 = requests.get(
                url_for("api.storage_shelves_onsite", id=id, _external=True),
                headers=get_internal_api_header(),
            )
            if response1.status_code == 200:
                #print(response1.json()["content"])
                shelves = response1.json()["content"]
                shelf_required = len(shelves) > 0

        form = EditSampleRackForm(shelves=shelves,
            data={"serial": rack["serial_number"], "description": rack["description"],
                  "storage_id": rack['storage_id'], "shelf_id": rack["shelf_id"]}
        )

        delattr(form, "num_cols")
        delattr(form, "num_rows")
        delattr(form, "colours")
        if not shelf_required:
            delattr(form, "shelf_id")

        if form.validate_on_submit():
            form_information = {
                "serial_number": form.serial.data,
                "description": form.description.data,
                "storage_id": form.storage_id.data
            }

            if shelf_required:
                form_information["shelf_id"] = form.shelf_id.data
            else:
                form_information["shelf_id"] = None

            edit_response = requests.put(
                url_for("api.storage_rack_edit", id=id, _external=True),
                headers=get_internal_api_header(),
                json=form_information,
            )

            if edit_response.status_code == 200:
                flash("Rack Successfully Edited")
            else:
                flash("We have a problem: %s" % (edit_response.json()))

            return redirect(url_for("storage.view_rack", id=id))

        return render_template(
            "storage/rack/edit.html", rack=response.json()["content"], form=form
        )

    abort(response.status_code)


