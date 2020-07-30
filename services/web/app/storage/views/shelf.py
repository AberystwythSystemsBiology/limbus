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

from ..models import *
from ...auth.views import UserView
from ...sample.views import BasicSampleView
from .cryobox import BasicCryoboxView


def BasicShelfView(shelf_id: int) -> dict:

    shelf = (
        db.session.query(FixedColdStorageShelf)
        .filter(FixedColdStorageShelf.id == shelf_id)
        .first_or_404()
    )

    return {
        "id": shelf.id,
        "name": shelf.name,
        "description": shelf.description,
        "storage_id": shelf.storage_id,
        "creation_date": shelf.creation_date,
        "update_date": shelf.update_date,
        "author_information": UserView(shelf.author_id),
    }


def ShelfView(shelf_id: int) -> dict:

    data = BasicShelfView(shelf_id)

    boxes = (
        db.session.query(EntityToStorage)
        .filter(
            EntityToStorage.shelf_id == shelf_id,
            EntityToStorage.storage_type == EntityToStorageTpye.BTS,
        )
        .all()
    )
    samples = (
        db.session.query(EntityToStorage)
        .filter(
            EntityToStorage.shelf_id == shelf_id,
            EntityToStorage.storage_type == EntityToStorageTpye.STS,
        )
        .all()
    )

    data["samples"] = {x.id: BasicSampleView(x.sample_id) for x in samples}
    data["cryoboxes"] = {x.id: BasicCryoboxView(x.box_id) for x in boxes}

    return data
