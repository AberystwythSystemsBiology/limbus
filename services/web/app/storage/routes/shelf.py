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

from .misc import move_entity_to_storage


from ..models import (
    FixedColdStorage,
    FixedColdStorageShelf,
    CryovialBox,
)
from ...sample.models import Sample

from ..forms import SampleToEntityForm, BoxToShelfForm, NewShelfForm
from ..views import ShelfView, BasicShelfView
from ..enums import EntityToStorageTpye
from uuid import uuid4

@storage.route("/shelves/LIMBSHF-<id>")
@login_required
def view_shelf(id):
    shelf = ShelfView(id)
    return render_template("storage/shelf/view.html", shelf=shelf)


@storage.route("/lts/LIMBLTS-<lts_id>/add_shelf", methods=["GET", "POST"])
@login_required
def add_shelf(lts_id):
    lts = (
        db.session.query(FixedColdStorage)
        .filter(FixedColdStorage.id == lts_id)
        .first_or_404()
    )

    form = NewShelfForm()

    if form.validate_on_submit():
        shelf = FixedColdStorageShelf(
            name=form.name.data,
            # Generate a UUID :)
            uuid=uuid4(),
            description=form.description.data,
            storage_id=lts_id,
            author_id=current_user.id,
        )

        db.session.add(shelf)
        db.session.commit()

        return redirect(url_for("storage.view_lts", lts_id=lts_id))

    return render_template("/storage/shelf/new.html", form=form, lts=lts)


@storage.route("/shelves/LIMBSHF-<id>/edit", methods=["GET", "POST"])
@login_required
def edit_shelf(id):
    shelf = BasicShelfView(id)

    form = NewShelfForm()

    if form.validate_on_submit():
        s = db.session.query(FixedColdStorageShelf).filter(FixedColdStorageShelf.id == id).first_or_404()

        s.name = form.name.data
        s.description = form.description.data
        s.author_id = current_user.id
        db.session.commit()
        flash("Shelf successfully updated.")

        return redirect(url_for("storage.view_shelf", id=id))

    form.name.data = shelf["name"]
    form.description.data = shelf["description"]

    return render_template("storage/shelf/edit.html", shelf=shelf, form=form)

@storage.route("/shelves/LIMBSHF-<shelf_id>/assign_box", methods=["GET", "POST"])
@login_required
def assign_box_to_shelf(shelf_id):
    shelf = ShelfView(shelf_id)

    form = BoxToShelfForm(db.session.query(CryovialBox).all())

    if form.validate_on_submit():
        move_entity_to_storage(
            box_id=form.boxes.data,
            shelf_id=shelf_id,
            entered=form.date.data.strftime("%Y-%m-%d, %H:%M:%S"),
            entered_by=form.entered_by.data,
            author_id=current_user.id,
            storage_type=EntityToStorageTpye.BTS,
        )

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

    form = SampleToEntityForm(samples)

    if form.validate_on_submit():

        sample = (
            db.session.query(Sample)
            .filter(Sample.id == form.samples.data)
            .first_or_404()
        )

        move_entity_to_storage(
            sample_id=sample.id,
            shelf_id=shelf_id,
            entered=form.date.data.strftime("%Y-%m-%d, %H:%M:%S"),
            entered_by=form.entered_by.data,
            author_id=current_user.id,
            storage_type=EntityToStorageTpye.STS,
        )

        flash("Sample assigned to shelf!")

        return redirect(url_for("storage.view_shelf", id=shelf.id))

    return render_template("storage/shelf/sample_to_shelf.html", form=form, shelf=shelf)
