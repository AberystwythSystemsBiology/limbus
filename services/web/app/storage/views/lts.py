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
from ..models.lts import *
from ..models.shelf import FixedColdStorageShelf
from ...auth.views import UserView
from .shelf import BasicShelfView


def BasicLTSView(lts_id: int) -> dict:
    lts = (
        db.session.query(FixedColdStorage)
        .filter(FixedColdStorage.id == lts_id)
        .first_or_404()
    )

    return {
        "id": lts_id,
        "serial_number": lts.serial_number,
        "manufacturer": lts.manufacturer,
        "type": lts.type,
        "room_id": lts.room_id,
        "temperature": lts.temperature,
        "creation_date": lts.creation_date,
        "update_date": lts.update_date,
        "author_information": UserView(lts.author_id),
    }


def LTSView(lts_id: int) -> dict:
    data = BasicLTSView(lts_id)

    data["shelves"] = {
        x.id: BasicShelfView(x.id)
        for x in db.session.query(FixedColdStorageShelf)
        .filter(FixedColdStorageShelf.storage_id == lts_id)
        .all()
    }

    return data
