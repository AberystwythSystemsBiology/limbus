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
    FixedColdStorageShelf,
    CryovialBox,
)
from ...sample.models import Sample

from ..forms import SampleToBoxForm, BoxToShelfForm
from ..views import ShelfView
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
        # move_cryovial_to_shelf(form.boxes.data, shelf_id)
        flash("LIMBCRB-%i successfully moved!" % (form.boxes.data))
        return redirect(url_for("storage.view_shelf", id=shelf_id))

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


        # TODO: Needs rewrite.
        return redirect(url_for("storage.view_shelf", id=shelf.id))

    return render_template("storage/shelf/sample_to_shelf.html", form=form, shelf=shelf)
