from flask import redirect, abort, render_template, url_for, session, request, jsonify, Response
from flask_login import current_user

from ... import db
from .. import storage

from ..models import (
    Site,
    Room,
    FixedColdStorage,
    CryovialBox,
    SampleToCryovialBox,
    CryovialBoxToFixedColdStorageShelf,
    FixedColdStorageShelf
)

from ..forms import NewCryovialBoxForm, SampleToBoxForm

from ...auth.models import User
from ...sample.models import Sample


@storage.route("/cryobox")
def cryobox_index():
    boxes = (
        db.session.query(CryovialBox, User)
        .filter(CryovialBox.author_id == User.id)
        .all()
    )
    return render_template("storage/cryobox/index.html", boxes=boxes)


@storage.route("/cryobox/view/LIMBCRB-<cryo_id>")
def view_cryobox(cryo_id):
    cryo = (
        db.session.query(CryovialBox).filter(CryovialBox.id == cryo_id).first_or_404()
    )
    return render_template("storage/cryobox/view.html", cryo=cryo)


@storage.route("/cryobox/view/LIMBCRB-<cryo_id>/data")
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


@storage.route(
    "/cryobox/add/sample/LIMCRB-<cryo_id>/<row>_<col>", methods=["GET", "POST"]
)
def add_cryobox_sample(cryo_id, row, col):
    cryo = (
        db.session.query(CryovialBox).filter(CryovialBox.id == cryo_id).first_or_404()
    )

    samples = db.session.query(Sample).all()

    form = SampleToBoxForm(samples)

    if form.validate_on_submit():
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


@storage.route("/cryobox/unassigned")
def list_unassigned():
    assigned_cryoboxes = db.session.query(CryovialBoxToFixedColdStorageShelf.box_id)
    cryobox_results = (
        db.session.query(CryovialBox)
        .filter(CryovialBox.id.in_(assigned_cryoboxes))
    )
    cryoboxes = [{'id': box.id, 'serial': box.serial} for box in cryobox_results]
    return jsonify(cryoboxes)

@storage.route("/cryobox/assign/LIMCRB-<cryo_id>", methods=["POST"])
def assign(cryo_id):
    data = request.get_json(force=True)
    if not data['id']:
        return Response("{'err':'No ID supplied', 'success': false}", status=201, mimetype='application/json')

    box = db.session.query(CryovialBox).filter(CryovialBox.id == cryo_id).first_or_404()
    shelf = db.session.query(FixedColdStorageShelf).filter(FixedColdStorageShelf.id == data['id']).first_or_404()

    box2shelf = CryovialBoxToFixedColdStorageShelf(
        box_id=box.id,
        shelf_id=shelf.id
    )

    existing_assignments = (
        db.session.query(CryovialBoxToFixedColdStorageShelf)
        .filter(CryovialBoxToFixedColdStorageShelf.box_id == cryo_id)
    )
    for assignment in existing_assignments:
        db.session.delete(assignment)

    db.session.add(box2shelf)
    db.session.commit()
    return jsonify({'success': True})