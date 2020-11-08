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
import requests
from ...misc import get_internal_api_header

from flask_login import current_user, login_required
from .. import storage

from ..forms import RoomRegistrationForm, RoomRegistrationForm

@storage.route("/building/LIMBBUILD-<id>/room/new", methods=["GET", "POST"])
@login_required
def new_room(id):
    
    response = requests.get(
        url_for("api.storage_building_view", id=id, _external=True),
        headers=get_internal_api_header()
    )

    if response.status_code == 200:
        form = RoomRegistrationForm()

        if form.validate_on_submit():

            new_response = requests.post(
                url_for("api.storage_room_new", _external=True),
                headers=get_internal_api_header(),
                json = {
                    "name": form.name.data,
                    "building_id": id
                }
            )

            if new_response.status_code == 200:
                flash("Room Successfully Created")
                # TODO: Replace.
                return redirect(url_for("document.index"))
            return abort(new_response.status_code)
        
        return render_template("storage/room/new.html", form=form, building=response.json()["content"])
    
    abort(response.status_code)

'''
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
'''