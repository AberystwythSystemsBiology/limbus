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
from ..enums import EntityToStorageType


from .room import *
from .lts import *
from .shelf import *
from .rack import *



class EntityToStorage(Base, RefAuthorMixin, RefEditorMixin):
    sample_id = db.Column(db.Integer, db.ForeignKey("sample.id"))
    box_id = db.Column(db.Integer, db.ForeignKey("samplebox.id"))
    shelf_id = db.Column(db.Integer, db.ForeignKey("coldstorageshelf.id"))
    storage_type = db.Column(db.Enum(EntityToStorageType))
    row = db.Column(db.Integer)
    col = db.Column(db.Integer)
    entry_datetime = db.Column(db.DateTime)
    entry = db.Column(db.String(5))
    removed = db.Column(db.Boolean)
