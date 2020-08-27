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
from ...mixins import RefAuthorMixin, RefEditorMixin, UniqueIdentifierMixin
from ..enums import FixedColdStorageTemps, FixedColdStorageType

class ColdStorage(Base, UniqueIdentifierMixin, RefAuthorMixin, RefEditorMixin):
    serial_number = db.Column(db.String)
    manufacturer = db.Column(db.String)
    comments = db.Column(db.Text)
    temp = db.Column(db.Enum(FixedColdStorageTemps))
    type = db.Column(db.Enum(FixedColdStorageType))
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"))

    documents = db.relationship("Document", secondary="documenttocoldstorage")


class DocumentToColdStorage(Base, RefAuthorMixin, RefEditorMixin):
    storage_id = db.Column(db.Integer, db.ForeignKey("coldstorage.id"))
    document_id = db.Column(db.Integer, db.ForeignKey("document.id"))