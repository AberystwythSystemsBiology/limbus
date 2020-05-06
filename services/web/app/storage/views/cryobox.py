from flask import redirect, abort, render_template, url_for, session, request, jsonify, Response
from flask_login import current_user, login_required

from ... import db
from .. import storage

from ..models import (
    Site,
    Room,
    FixedColdStorage,
    CryovialBox,
    SampleToCryovialBox,
    CryovialBoxToFixedColdStorageShelf,
    FixedColdStorageShelf,
    SampleToFixedColdStorageShelf
)

from ..forms import NewCryovialBoxForm, SampleToBoxForm

from ...auth.models import User
from ...sample.models import Sample


@storage.route("/cryobox")
@login_required
def cryobox_index():
    boxes = (
        db.session.query(CryovialBox, User)
        .filter(CryovialBox.author_id == User.id)
        .all()
    )
    return render_template("storage/cryobox/index.html", boxes=boxes)


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
        }

    return jsonify(data), 201, {"Content-Type": "application/json"}


@storage.route("cryobox/add/sample/LIMCRB-<cryo_id>/<row>_<col>", methods=["GET", "POST"])
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
