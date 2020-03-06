from flask import redirect, abort, render_template, url_for, session, request, jsonify
from flask_login import current_user

from ... import db
from .. import storage

from ..models import Room, Site, FixedColdStorage, FixedColdStorageShelf
from ...auth.models import User

from ..forms import LongTermColdStorageForm, NewShelfForm


@storage.route("lts/")
def lts_index():
    lts = (
        db.session.query(FixedColdStorage, User, Site)
        .filter(User.id == FixedColdStorage.author_id)
        .filter(FixedColdStorage.site_id == Site.id)
        .all()
    )

    return render_template("storage/lts/index.html", lts=lts)


@storage.route("lts/add", methods=["GET", "POST"])
def add_lts():
    rs_query = db.session.query(Room, Site).filter(Room.site_id == Site.id).all()

    form = LongTermColdStorageForm(rs_query)

    if form.validate_on_submit():
        print(int(form.location.data))
        print(rs_query[int(form.location.data)])
        fcs = FixedColdStorage(
            serial_number=form.serial_number.data,
            manufacturer=form.manufacturer.data,
            temperature=form.temperature.data,
            type=form.type.data,
            site_id=rs_query[int(form.location.data)][1].id,
            author_id=current_user.id,
        )

        db.session.add(fcs)
        db.session.commit()
        return redirect(url_for("storage.lts_index"))

    return render_template("storage/lts/new.html", form=form)


@storage.route("/lts/view/LIMBLTS-<lts_id>", methods=["GET", "POST"])
def view_lts(lts_id):
    lts = (
        db.session.query(FixedColdStorage)
        .filter(FixedColdStorage.id == lts_id)
        .first_or_404()
    )

    shelves = db.session.query(FixedColdStorageShelf, User).filter(FixedColdStorageShelf.storage_id == lts_id).filter(User.id == FixedColdStorageShelf.author_id).all()

    form = NewShelfForm()

    if form.validate_on_submit():
        shelf = FixedColdStorageShelf(
            name = form.name.data,
            storage_id = lts_id,
            author_id = current_user.id
        )

        db.session.add(shelf)
        db.session.commit()

        return redirect(url_for("storage.view_lts", lts_id))

    return render_template("/storage/lts/view.html", lts=lts, form=form, shelves=shelves)
