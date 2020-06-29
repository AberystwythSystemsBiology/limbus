from flask import (
    redirect,
    abort,
    render_template,
    url_for,
    session,
    request,
    jsonify,
    Response,
)
from flask_login import current_user, login_required

from ... import db
from .. import storage

from ...misc.generators import generate_random_hash

import csv

from ..models import (
    Site,
    Room,
    FixedColdStorage,
    CryovialBox,
    SampleToCryovialBox,
    CryovialBoxToFixedColdStorageShelf,
    FixedColdStorageShelf,
    SampleToFixedColdStorageShelf,
)

from ..forms import NewCryovialBoxForm, SampleToBoxForm, NewCryovialBoxFileUploadForm, CryoBoxFileUploadSelectForm

from ...auth.models import User
from ...sample.models import Sample

def file_to_json(form) -> dict:
    data = {}

    csv_data = [x.decode("UTF-8").replace("\n", "").split(",") for x in form.file.data.stream]

    # Get Indexes
    indexes = {
        "Tube Barcode": csv_data[0].index("Tube Barcode"),
        "Tube Position": csv_data[0].index("Tube Position")
    }

    positions = {x[indexes["Tube Position"]]: x[indexes["Tube Barcode"]] for x in csv_data[1:]}

    data["positions"] = positions
    data["serial_number"] = form.serial.data

    return data



@storage.route("/cryobox")
@login_required
def cryobox_index():
    boxes = (
        db.session.query(CryovialBox, User)
        .filter(CryovialBox.author_id == User.id)
        .all()
    )
    return render_template("storage/cryobox/index.html", boxes=boxes)


@storage.route("/cryobox/new", methods=["GET", "POST"])
@login_required
def add_cryobox():
    return render_template("storage/cryobox/new/option.html")


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
            "sample": db.session.query(Sample).filter(Sample.biobank_barcode == barcode).first()
        }



    form = CryoBoxFileUploadSelectForm(sample_data)
    return render_template("storage/cryobox/new/from_file/step_two.html", form=form, hash=hash)


@storage.route("/cryobox/view/LIMBCRB-<cryo_id>")
@login_required
def view_cryobox(cryo_id):
    cryo = (
        db.session.query(CryovialBox).filter(CryovialBox.id == cryo_id).first_or_404()
    )
    return render_template("storage/cryobox/view.html", cryo=cryo)


@storage.route("/cryobox/view/LIMBCRB-<cryo_id>/data")
@login_required
def view_cryobox_api(cryo_id):
    cryo = (
        db.session.query(CryovialBox).filter(CryovialBox.id == cryo_id).first_or_404()
    )

    samples = (
        db.session.query(SampleToCryovialBox, Sample, User)
        .filter(SampleToCryovialBox.box_id == cryo_id)
        .filter(Sample.id == SampleToCryovialBox.sample_id)
        .filter(Sample.author_id == User.id)
        .all()
    )

    data = {}
    for position, sample, user in samples:
        data["%i_%i" % (position.row, position.col)] = {
            "id": sample.id,
            "url": url_for("sample.view", sample_id=sample.id, _external=True),
            "barcode": url_for("sample.get_barcode", sample_id=sample.id, attr="uuid", _external=True)
        }

    return jsonify(data), 201, {"Content-Type": "application/json"}


@storage.route(
    "cryobox/add/sample/LIMCRB-<cryo_id>/<row>_<col>", methods=["GET", "POST"]
)
@login_required
def add_cryobox_sample(cryo_id, row, col):
    cryo = (
        db.session.query(CryovialBox).filter(CryovialBox.id == cryo_id).first_or_404()
    )

    samples = db.session.query(Sample).all()

    form = SampleToBoxForm(samples)

    if form.validate_on_submit():
        sample = (
            db.session.query(Sample)
            .filter(Sample.id == form.samples.data)
            .first_or_404()
        )

        sample_shelf_binds = (
            db.session.query(SampleToFixedColdStorageShelf)
            .filter(SampleToFixedColdStorageShelf.sample_id == sample.id)
            .all()
        )

        sample_box_binds = (
            db.session.query(SampleToCryovialBox)
            .filter(SampleToCryovialBox.sample_id == sample.id)
            .all()
        )

        for bind in sample_shelf_binds + sample_box_binds:
            db.session.delete(bind)

        scb = SampleToCryovialBox(
            sample_id=form.samples.data,
            box_id=cryo_id,
            col=col,
            row=row,
            author_id=current_user.id,
        )

        db.session.add(scb)
        db.session.commit()

        return redirect(url_for("storage.view_cryobox", cryo_id=cryo_id))

    return render_template(
        "storage/cryobox/sample_to_box.html", cryo=cryo, form=form, row=row, col=col
    )
