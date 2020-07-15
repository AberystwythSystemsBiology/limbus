from flask import redirect, abort, render_template, url_for, session, request, jsonify

from flask_login import current_user, login_required
from ... import db
from .. import storage

from ..forms import SiteRegistrationForm, RoomRegistrationForm, LongTermColdStorageForm

from ..models import (
    Site,
    Room,
    FixedColdStorage,
    FixedColdStorageShelf,
)

from ...misc.models import Address
from ...auth.models import User

from ..views.room import RoomView


@storage.route("rooms/new", methods=["GET", "POST"])
@login_required
def add_room():
    form = SiteRegistrationForm()
    if form.validate_on_submit():

        addr = Address(
            street_address_one=form.address_line_one.data,
            street_address_two=form.address_line_two.data,
            city=form.city.data,
            county=form.county.data,
            post_code=form.post_code.data,
            country=form.country.data,
        )

        db.session.add(addr)

        db.session.flush()

        site = Site(name=form.name.data, address_id=addr.id, author_id=current_user.id)

        db.session.add(site)
        db.session.commit()

        return redirect(url_for("storage.site_index"))

    return render_template("storage/site/new.html", form=form)


@storage.route("/rooms/LIMBROM-<room_id>")
@login_required
def view_room(room_id: int):
    room = RoomView(room_id)
    return render_template("storage/room/view.html", room=room)



@storage.route("/rooms/add_lts/LIMBROM-<id>", methods=["GET", "POST"])
@login_required
def add_lts(id):
    room = db.session.query(Room).filter(Room.id == id).first_or_404()
    form = LongTermColdStorageForm()

    if form.validate_on_submit():
        fcs = FixedColdStorage(
            serial_number=form.serial_number.data,
            manufacturer=form.manufacturer.data,
            temperature=form.temperature.data,
            type=form.type.data,
            room_id=id,
            author_id=current_user.id,
        )

        db.session.add(fcs)
        db.session.commit()
        return redirect(url_for("storage.view_room", id=id))

    return render_template("storage/lts/new.html", form=form, room=room)
