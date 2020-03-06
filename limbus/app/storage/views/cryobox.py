from flask import redirect, abort, render_template, url_for, session, request, jsonify
from flask_login import current_user

from ... import db
from .. import storage

from ..models import CryovialBox
from ..forms import NewCryovialBoxForm

@storage.route("/cryobox")
def cryobox_index():
    boxes = db.session.query(CryovialBox).all()

    return render_template("storage/cryobox/index.html", boxes=boxes)

@storage.route("/cryobox/new", methods=["GET", "POST"])
def add_cryobox():
    form = NewCryovialBoxForm()

    if form.validate_on_submit():

        cb = CryovialBox(
            serial = form.serial.data,
            num_rows = form.num_rows.data,
            num_cols = form.num_cols.data,
            data = {},
            author_id = current_user.id
        )

        db.session.add(cb)
        db.session.commit()

        return redirect(url_for("storage.cryobox_index"))

    return render_template("storage/cryobox/new.html", form=form)