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

    def __generate_data(n_cols, n_rows):
        columns = {"column %i" % (c): None for c in range(n_cols)}

        data = {
            "row %i" % (r): columns for r in range(n_rows)
        }

        return data

    form = NewCryovialBoxForm()

    if form.validate_on_submit():

        cb = CryovialBox(
            serial=form.serial.data,
            num_rows=form.num_rows.data,
            num_cols=form.num_cols.data,
            data=__generate_data(form.num_cols.data, form.num_rows.data),
            author_id=current_user.id,
        )

        db.session.add(cb)
        db.session.commit()

        return redirect(url_for("storage.cryobox_index"))

    return render_template("storage/cryobox/new.html", form=form)

@storage.route("/cryobox/view/LIMBCR-<cryo_id>")
def view_cryobox(cryo_id):
    cryo = db.session.query(CryovialBox).filter(CryovialBox.id == cryo_id).first_or_404()
    return "Hello World"

@storage.route("/cryobox/view/LIMBCR-<cryo_id>/data")
def view_cryobox_api(cryo_id):
    cryo = db.session.query(CryovialBox).filter(CryovialBox.id == cryo_id).first_or_404()
    return jsonify(cryo.data), 201, {"Content-Type": "application/json"}
