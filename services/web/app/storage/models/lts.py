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
from ..enums import (
    FixedColdStorageTemps,
    FixedColdStorageType,
    ColdStorageServiceResult,
    FixedColdStorageStatus,
)


class ColdStorage(Base, UniqueIdentifierMixin, RefAuthorMixin, RefEditorMixin):
    __versioned__ = {}
    alias = db.Column(db.String(128))
    serial_number = db.Column(db.String(128))
    manufacturer = db.Column(db.String(128))
    comments = db.Column(db.Text)
    status = db.Column(db.Enum(FixedColdStorageStatus))
    temp = db.Column(db.Enum(FixedColdStorageTemps))
    type = db.Column(db.Enum(FixedColdStorageType))
    room_id = db.Column(db.Integer, db.ForeignKey("room.id"))
    shelves = db.relationship("ColdStorageShelf")
    room = db.relationship("Room")
    documents = db.relationship("Document", secondary="documenttocoldstorage")
    service_history = db.relationship("ColdStorageService")


class ColdStorageService(Base, UniqueIdentifierMixin, RefAuthorMixin, RefEditorMixin):
    __versioned__ = {}

    date = db.Column(db.Date)
    conducted_by = db.Column(db.String(128))
    temp = db.Column(db.Integer)
    status = db.Column(db.Enum(ColdStorageServiceResult))
    comments = db.Column(db.Text)

    storage_id = db.Column(db.Integer, db.ForeignKey("coldstorage.id"))


class DocumentToColdStorageService(Base, RefAuthorMixin, RefEditorMixin):
    __versioned__ = {}
    service_id = db.Column(db.Integer, db.ForeignKey("coldstorageservice.id"))
    document_id = db.Column(db.Integer, db.ForeignKey("document.id"))


class DocumentToColdStorage(Base, RefAuthorMixin, RefEditorMixin):
    __versioned__ = {}
    storage_id = db.Column(db.Integer, db.ForeignKey("coldstorage.id"))
    document_id = db.Column(db.Integer, db.ForeignKey("document.id"))
