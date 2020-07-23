from flask import redirect, abort, render_template, url_for, session, request, jsonify, flash

from flask_login import current_user, login_required
from ... import db
from .. import storage

from ..forms import RoomRegistrationForm, LongTermColdStorageForm

from ..models import (
    FixedColdStorage,
    Room
)


from ..views.room import RoomView, BasicRoomView

@storage.route("/rooms/LIMBROM-<room_id>")
@login_required
def view_room(room_id: int):
    room = RoomView(room_id)
    return render_template("storage/room/view.html", room=room)


@storage.route("/rooms/LIMBROM-<room_id>/edit", methods=["GET", "POST"])
@login_required
def edit_room(room_id: int):
    form = RoomRegistrationForm()
    if form.validate_on_submit():
        r = db.session.query(Room).filter(Room.id == room_id).first_or_404()

        r.room_number = form.room.data
        r.building = form.building.data,
        r.author_id = current_user.id

        db.session.commit()

        flash("LIMBROM-%s successfully updated." % (room_id))

        return redirect(url_for("storage.view_room", room_id=room_id))

    room = BasicRoomView(room_id)
    form.room.data = room["room_number"]
    form.building.data = room["building"]
    return render_template("storage/room/edit.html", form=form, room=room)

@storage.route("/rooms/add_storage/LIMBROM-<room_id>", methods=["GET", "POST"])
@login_required
def add_lts(room_id: int):
    room = BasicRoomView(room_id)
    form = LongTermColdStorageForm()

    if form.validate_on_submit():
        fcs = FixedColdStorage(
            serial_number=form.serial_number.data,
            manufacturer=form.manufacturer.data,
            temperature=form.temperature.data,
            type=form.type.data,
            room_id=room_id,
            author_id=current_user.id,
        )

        db.session.add(fcs)
        db.session.commit()
        return redirect(url_for("storage.view_room", room_id=room_id))

    return render_template("storage/lts/new.html", form=form, room=room)
