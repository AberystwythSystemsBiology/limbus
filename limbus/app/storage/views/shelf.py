from flask import redirect, abort, render_template, url_for, session, request, jsonify

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
