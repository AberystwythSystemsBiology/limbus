from flask import redirect, abort, render_template, url_for, session, request, jsonify
from flask_login import current_user, login_required

from ... import db
from .. import storage

from ..models import (
    Site,
    Room,
    FixedColdStorage,
    FixedColdStorageShelf,
)
from ...auth.models import User
from ...sample.models import Sample
from uuid import uuid4

from ..forms import NewShelfForm


@storage.route("/lts/view/LIMBLTS-<lts_id>", methods=["GET"])
@login_required
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

    """

    for shelf, user_info in shelves:
        samples = (
            db.session.query(SampleToFixedColdStorageShelf, Sample)
            .filter(SampleToFixedColdStorageShelf.shelf_id == shelf.id)
            .filter(Sample.id == SampleToFixedColdStorageShelf.sample_id)
            .all()
        )

        _shelves[shelf.id] = {"shelf_information": shelf, "samples": samples}
    """

    return render_template("/storage/lts/view.html", lts=lts, shelves=_shelves)

