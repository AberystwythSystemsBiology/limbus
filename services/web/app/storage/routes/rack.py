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
import requests
from ...misc import get_internal_api_header

from ..forms import NewSampleRackForm

'''

def iter_all_strings():
    for size in itertools.count(1):
        for s in itertools.product(ascii_uppercase, repeat=size):
            yield "".join(s)


values = []
for i in iter_all_strings():
    values.append(i)
    if i == "ZZZ":
        break


def file_to_json(form) -> dict:
    data = {}

    csv_data = [
        x.decode("UTF-8").replace("\n", "").split(",") for x in form.file.data.stream
    ]

    # Get Indexes
    indexes = {
        "Tube Barcode": csv_data[0].index("Tube Barcode"),
        "Tube Position": csv_data[0].index("Tube Position"),
        "Tube Row": [],
        "Tube Column": [],
    }

    positions = {
        x[indexes["Tube Position"]]: x[indexes["Tube Barcode"]] for x in csv_data[1:]
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
    data["serial_number"] = form.serial.data

    return data

'''

@storage.route("/rack")
@login_required
def rack_index():
    response = requests.get(
        url_for("api.storage_rack_home", _external=True),
        headers=get_internal_api_header()
    )

    if response.status_code == 200:
         return render_template("storage/rack/index.html", racks=response.json()["content"])


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
                "description": form.description.data
            }
        )

        if response.status_code == 200:
            flash("Sample Rack Added")
            return redirect(url_for("storage.rack_index"))

    return render_template("storage/rack/new/manual/new.html", form=form)


"""

@storage.route("/cryobox/new/from_file", methods=["GET", "POST"])
@login_required
def cryobox_from_file():
    form = NewCryovialBoxFileUploadForm()
    if form.validate_on_submit():
        hash = generate_random_hash()
        session[hash] = file_to_json(form)
        return redirect(url_for("storage.crybox_from_file_validation", hash=hash))
    return render_template("storage/cryobox/new/from_file/step_one.html", form=form)


@storage.route("/cryobox/new/from_file/validation/<hash>", methods=["GET", "POST"])
@login_required
def crybox_from_file_validation(hash: str):
    session_data = session[hash]

    sample_data = {}

    for position, barcode in session_data["positions"].items():
        sample_data[position] = {
            "barcode": barcode,
            "sample": db.session.query(Sample)
            .filter(Sample.biobank_barcode == barcode)
            .first(),
        }

    form = CryoBoxFileUploadSelectForm(sample_data)

    if form.validate_on_submit():

        cry = CryovialBox(
            serial=session_data["serial_number"],
            num_rows=session_data["num_rows"],
            num_cols=session_data["num_cols"],
            author_id=current_user.id,
        )

        db.session.add(cry)
        db.session.flush()

        for ele in form:
            if ele.type == "BooleanField":
                if ele.data:
                    regex = re.compile(r"(\d+|\s+)")
                    col, row, _ = regex.split(ele.id)
                    sample_id = ele.render_kw["_sample"].id

        db.session.commit()
        clear_session(hash)
        return redirect(url_for("storage.cryobox_index"))
    return render_template(
        "storage/cryobox/new/from_file/step_two.html",
        form=form,
        hash=hash,
        session_data=session_data,
    )

"""
@storage.route("/rack/LIMBRACK-<id>")
@login_required
def view_rack(id):
    return render_template("storage/rack/view.html", id=id)


@storage.route("/rack/LIMBRACK-<id>/endpoint")
@login_required
def view_rack_endpoint(id):
    view_response = requests.get(
        url_for("api.storage_rack_view", id=id, _external=True),
        headers=get_internal_api_header()
    )

    if view_response.status_code == 200:
        return view_response.json()
    return abort(view_response.status_code)



@storage.route("rack/LIMBRACK-<id>/edit", methods=["GET", "POST"])
@login_required
def edit_rack(id):

    response = requests.get(
        url_for("api.storage_rack_view", id=id, _external=True),
        headers=get_internal_api_header()
    )

    if response.status_code == 200:
        rack = response.json()["content"]

        form = NewSampleRackForm(
            data={
                "serial": rack["serial_number"],
                "description": rack["description"]
                }
        )

        delattr(form, "num_cols")
        delattr(form, "num_rows")
        delattr(form, "colours")

        if form.validate_on_submit():
            form_information = {
                "serial_number": form.serial.data,
                "description": form.description.data
            }

            edit_response = requests.put(
                url_for("api.storage_rack_edit", id=id, _external=True),
                headers=get_internal_api_header(),
                json=form_information,
            )

            if edit_response.status_code == 200:
                flash("Shelf Successfully Edited")
            else:
                flash("We have a problem: %s" % (edit_response.json()))
            
            return redirect(url_for("storage.view_rack", id=id))


        return render_template("storage/rack/edit.html", rack=response.json()["content"], form=form)


    abort(response.status_code)
    
    '''
    form = NewCryovialBoxForm()
    delattr(form, "num_cols")
    delattr(form, "num_rows")


    if form.validate_on_submit():
        cb = db.session.query(CryovialBox).filter(CryovialBox.id == cryo_id).first()
        print(">>>>>>>>>>>>>>>", form.serial.data)
        cb.serial = form.serial.data
        db.session.add(cb)
        db.session.commit()
        flash("Cryobox information successfully edited!")
        return redirect(url_for("storage.view_cryobox", cryo_id=cryo_id))

    form.serial.data = cryo["info"]["serial"]
    return render_template("storage/cryobox/edit.html", cryo=cryo, form=form)
    '''

"""
# TODO: All of this needs to be given a specific view.
from sqlalchemy_continuum import version_class
from sqlalchemy import desc


@storage.route("/history/LIMB<storage_type>-<id>/")
@login_required
def view_history(storage_type, id):
    EntityToStorageVersioned = version_class(EntityToStorage)
    if storage_type == "CRB":
        attr = "box_id"
    elif storage_type == "SHF":
        attr = "shelf_id"
    elif storage_type == "SMP":
        attr = "sample_id"

    changes = {}

    for change in (
        db.session.query(EntityToStorageVersioned)
        .filter(getattr(EntityToStorageVersioned, attr) == id)
        .order_by(desc(EntityToStorageVersioned.update_date))
        .all()
    ):
        changes[change.id] = {
            "sample_id": change.sample_id,
            "box_id": change.box_id,
            "shelf_id": change.shelf_id,
            "storage_type": change.storage_type.value,
            "row": change.row,
            "col": change.col,
            "entered_by": change.entered_by,
            "entered": change.entered,
            "update_date": change.update_date,
            "author_information": UserView(change.author_id),
        }

    return render_template(
        "storage/history.html", storage_type=storage_type, id=id, changes=changes
    )




@storage.route(
    "cryobox/add/sample/LIMCRB-<cryo_id>/<row>_<col>", methods=["GET", "POST"]
)
@login_required
def add_cryobox_sample(cryo_id, row, col):
    cryo = (
        db.session.query(CryovialBox).filter(CryovialBox.id == cryo_id).first_or_404()
    )

    samples = db.session.query(Sample).all()

    form = SampleToEntityForm(samples)

    if form.validate_on_submit():
        sample = (
            db.session.query(Sample)
            .filter(Sample.id == form.samples.data)
            .first_or_404()
        )

        move_entity_to_storage(
            sample_id=sample.id,
            box_id=cryo_id,
            row=row,
            col=col,
            entered=form.date.data.strftime("%Y-%m-%d, %H:%M:%S"),
            entered_by=form.entered_by.data,
            author_id=current_user.id,
            storage_type=EntityToStorageTpye.STB,
        )

        flash("Sample assigned to shelf!")
        return redirect(url_for("storage.view_cryobox", cryo_id=cryo_id))

    return render_template(
        "storage/cryobox/sample_to_box.html", cryo=cryo, form=form, row=row, col=col
    )
"""
