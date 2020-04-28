from flask import redirect, abort, render_template, url_for, session, request, jsonify
from flask_login import current_user

from ... import db
from .. import storage

from ..models import (
    Site,
    Room,
    FixedColdStorage,
    FixedColdStorageShelf,
    SampleToFixedColdStorageShelf
)
from ...auth.models import User
from ...sample.models import Sample

from ..forms import NewShelfForm


@storage.route("/lts/view/LIMBLTS-<lts_id>", methods=["GET", "POST"])
def view_lts(lts_id):
    lts = (
        db.session.query(FixedColdStorage)
        .filter(FixedColdStorage.id == lts_id)
        .first_or_404()
    )

    shelves = (
        db.session.query(FixedColdStorageShelf, User)
        .filter(FixedColdStorageShelf.storage_id == lts_id)
        .filter(User.id == FixedColdStorageShelf.author_id)
        .all()
    )

    _shelves = {}

    for shelf, user_info in shelves:
        samples = (
            db.session.query(SampleToFixedColdStorageShelf, Sample)
            .filter(SampleToFixedColdStorageShelf.shelf_id == shelf.id)
            .filter(Sample.id == SampleToFixedColdStorageShelf.sample_id)
            .all()
        )

        _shelves[shelf.id] = {"shelf_information": shelf, "samples": samples}

    form = NewShelfForm()

    if form.validate_on_submit():
        shelf = FixedColdStorageShelf(
            name=form.name.data, storage_id=lts_id, author_id=current_user.id
        )

        db.session.add(shelf)
        db.session.commit()

        return redirect(url_for("storage.view_lts", lts_id=lts_id))

    return render_template(
        "/storage/lts/view.html", lts=lts, form=form, shelves=_shelves
    )
