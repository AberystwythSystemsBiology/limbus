from flask import redirect, abort, render_template, url_for, session, request, jsonify
from flask_login import current_user

from ... import db
from .. import storage

from ..models import Room, Site, FixedColdStorage
from ...auth.models import User

from ..forms import LongTermColdStorageForm


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
