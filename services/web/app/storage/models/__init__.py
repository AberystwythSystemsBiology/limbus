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

from ...database import db, Base
from ...mixins import RefAuthorMixin, RefEditorMixin

from .site import *
from .room import *
from .lts import *
from .shelf import *
from .cryobox import *

from ..enums import EntityToStorageTpye


class EntityToStorage(Base, RefAuthorMixin, RefEditorMixin):
    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))
    box_id = db.Column(db.Integer, db.ForeignKey("cryovial_boxes.id"))
    shelf_id = db.Column(db.Integer, db.ForeignKey("fixed_cold_storage_shelves.id"))
    storage_type = db.Column(db.Enum(EntityToStorageTpye))
    row = db.Column(db.Integer)
    col = db.Column(db.Integer)
    entered_datetime = db.Column(db.DateTime)
    entered_by = db.Column(db.String(5))
    removed = db.Column(db.Boolean)
