from flask import redirect, abort, render_template, url_for, session, request, jsonify
from flask_login import current_user

from ... import db
from .. import storage


from ..models import (
    Site,
    Room,
    FixedColdStorage,
    FixedColdStorageShelf,
    SampleToFixedColdStorageShelf,
    CryovialBox,
    CryovialBoxToFixedColdStorageShelf
)
from ...sample.models import Sample

from ...misc.models import Address
from ...auth.models import User
from ..forms import NewCryovialBoxForm


@storage.route("/shelves/view/LIMBSHF-<id>")
def view_shelf(id):
    shelf = db.session.query(FixedColdStorageShelf).filter(FixedColdStorageShelf.id == id).first_or_404()
    samples = (
        db.session.query(SampleToFixedColdStorageShelf)
        .filter(SampleToFixedColdStorageShelf.shelf_id == id)
        .join(FixedColdStorageShelf)
        .all()
    )

    cryoboxes = (
        db.session.query(CryovialBox)
        .join(CryovialBoxToFixedColdStorageShelf)
        .filter(CryovialBoxToFixedColdStorageShelf.shelf_id == id)
        .all()
    )

    return render_template(
        "storage/shelf/view.html",
        shelf=shelf,
        samples=samples,
        cryoboxes=cryoboxes
    )


@storage.route("/shelves/add_cryobox/LIMBSHF-<shelf_id>", methods=["GET", "POST"])
def add_cryobox(shelf_id):
    shelf = (
        db.session.query(FixedColdStorageShelf)
                  .filter(FixedColdStorageShelf.id == shelf_id)
                  .first_or_404()
    )
    form = NewCryovialBoxForm()

    if form.validate_on_submit():

        cb = CryovialBox(
            serial=form.serial.data,
            num_rows=form.num_rows.data,
            num_cols=form.num_cols.data,
            author_id=current_user.id,
        )

        db.session.add(cb)
        db.session.flush()

        cbfcs = CryovialBoxToFixedColdStorageShelf(
            box_id=cb.id, shelf_id=shelf_id, author_id=current_user.id
        )

        db.session.add(cbfcs)

        db.session.commit()

        return redirect(url_for("storage.view_shelf", id=shelf.id))

    return render_template("storage/cryobox/new.html", form=form, shelf=shelf)
