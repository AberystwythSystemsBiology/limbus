from flask import (
    redirect,
    abort,
    render_template,
    url_for,
    session,
    request,
    jsonify,
    flash,
)
from flask_login import current_user, login_required

from ... import db
from .. import storage


from ..models import (
    Site,
    Room,
    FixedColdStorage,
    FixedColdStorageShelf,
    SampleToFixedColdStorageShelf,
    CryovialBox,
    CryovialBoxToFixedColdStorageShelf,
    SampleToCryovialBox,
)
from ...sample.models import Sample

from ...misc.models import Address
from ...auth.models import User
from ..forms import NewCryovialBoxForm, SampleToBoxForm, BoxToShelfForm

from ..views import ShelfView, BasicCryoboxView

from ...misc import chunks


@storage.route("/shelves/view/LIMBSHF-<id>")
@login_required
def view_shelf(id):
    shelf = ShelfView(id)

    # Conversion to make it renderable in a nice way.
    shelf["cryoboxes"] = chunks([x for x in shelf["cryoboxes"].items()], 4)

    return render_template("storage/shelf/view.html", shelf=shelf)


@storage.route("/shelves/LIMBSHF-<shelf_id>/assign_box", methods=["GET", "POST"])
@login_required
def assign_box_to_shelf(shelf_id):
    shelf = ShelfView(shelf_id)

    form = BoxToShelfForm(db.session.query(CryovialBox).all())

    if form.validate_on_submit():
        cbtfcss = CryovialBoxToFixedColdStorageShelf(
            shelf_id=shelf_id, box_id=form.boxes.data, author_id=current_user.id
        )

        db.session.add(cbtfcss)
        db.session.commit()

        flash("LIMBCRB-%i successfully moved!" % (form.boxes.data))

        return redirect(url_for("storage.view_shelf", id=shelf_Cid))

    return render_template("/storage/shelf/box_to_shelf.html", shelf=shelf, form=form)


@storage.route("/shelves/LIMBSHF-<shelf_id>/assign_sample", methods=["GET", "POST"])
@login_required
def assign_sample_to_shelf(shelf_id):
    shelf = (
        db.session.query(FixedColdStorageShelf)
        .filter(FixedColdStorageShelf.id == shelf_id)
        .first_or_404()
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

        sfcs = SampleToFixedColdStorageShelf(
            sample_id=sample.id, shelf_id=shelf.id, author_id=current_user.id
        )

        db.session.add(sfcs)
        db.session.commit()

        return redirect(url_for("storage.view_shelf", id=shelf.id))

    return render_template("storage/shelf/sample_to_shelf.html", form=form, shelf=shelf)
