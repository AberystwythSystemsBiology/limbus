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
from ..models import CryovialBox, EntityToStorage
from ..enums import EntityToStorageTpye
from ...auth.views import UserView
from ...sample.views import BasicSampleView


def CryoboxIndexView() -> dict:
    boxes = db.session.query(CryovialBox).all()

    data = {}

    for b in boxes:
        d = BasicCryoboxView(b.id)
        del d["id"]
        data[b.id] = d

    return data


def BasicCryoboxView(cryo_id: int) -> dict:
    box = db.session.query(CryovialBox).filter(CryovialBox.id == cryo_id).first_or_404()

    return {
        "id": cryo_id,
        "serial": box.serial,
        "num_rows": box.num_rows,
        "num_cols": box.num_cols,
        "author_information": UserView(box.author_id),
    }


def CryoboxView(cryo_id: int) -> dict:
    data = {}

    data["info"] = BasicCryoboxView(cryo_id)
    data["sample_information"] = {}

    for sample in (
        db.session.query(EntityToStorage)
        .filter(
            EntityToStorage.box_id == cryo_id,
            EntityToStorage.storage_type == EntityToStorageTpye.STB,
        )
        .all()
    ):
        data["sample_information"][
            "%i_%i" % (sample.row, sample.col)
        ] = BasicSampleView(sample.sample_id)

    return data
