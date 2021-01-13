# Copyright (C) 2019 Keiron O'Shea <keo7@aber.ac.uk>
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
from uuid import uuid4


class SampleProtocolEvent(Base, UniqueIdentifierMixin, RefAuthorMixin, RefEditorMixin):
    __versioned__ = {}

    datetime = db.Column(db.DateTime)
    undertaken_by = db.Column(db.String(128))
    comments = db.Column(db.Text)

    sample_id = db.Column(db.Integer, db.ForeignKey("sample.id"))

    protocol_id = db.Column(db.Integer, db.ForeignKey("protocoltemplate.id"))
    protocol = db.relationship("ProtocolTemplate")

    # -- Use the same uuid to reference the same protocol event,
    # e.g. for aliquot/derivation events, where the parent/child samples share the same event uuid
    uuid = db.Column(db.String(36), default=uuid4, nullable=False, unique=False)
