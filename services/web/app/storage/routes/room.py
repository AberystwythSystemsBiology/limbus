# Copyright (C) 2019  Keiron O'Shea <keo7@aber.ac.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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

from ..forms import RoomRegistrationForm, LongTermColdStorageForm

from ..models import FixedColdStorage, Room


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
        r.building = (form.building.data,)
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
