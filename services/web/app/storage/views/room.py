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

from ... import db
from ..models.room import Room
from ..models.lts import FixedColdStorage
from ...auth.views import UserView
from .lts import BasicLTSView


def BasicRoomView(room_id: int) -> dict:
    r = db.session.query(Room).filter(Room.id == room_id).first_or_404()
    return {
        "id": r.id,
        "room_number": r.room_number,
        "building": r.building,
        "creation_date": r.creation_date,
        "site_id": r.site_id,
        "author_information": UserView(r.author_id),
    }


def RoomView(room_id: int) -> dict:
    data = BasicRoomView(room_id)

    data["storage"] = [
        BasicLTSView(x.id)
        for x in db.session.query(FixedColdStorage)
        .filter(FixedColdStorage.room_id == room_id)
        .all()
    ]

    return data
