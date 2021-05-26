# Copyright (C) 2021  Keiron O'Shea <keo7@aber.ac.uk>
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
from ..enums import SampleShipmentStatusStatus

class UserCart(Base, RefAuthorMixin, RefEditorMixin):
    sample_id = db.Column(db.Integer, db.ForeignKey("sample.id"))



class SampleShipmentEventStatus(Base, RefAuthorMixin, RefEditorMixin):
    event_id = db.Column(db.Integer, db.ForeignKey("sampleshipmentevent.id"))
    status = db.Column(db.Enum(SampleShipmentStatusStatus))
    comments = db.Column(db.Text())
    datetime = db.Column(db.DateTime)


class SampleShipmentEvent(Base, RefAuthorMixin, RefEditorMixin):
    __versioned__ = {}

    sample_id = db.Column(db.Integer, db.ForeignKey("sample.id"), unique=True, primary_key=True)
    from_site_id = db.Column(db.Integer, db.ForeignKey("siteinformation.id"))
    to_site_id = db.Column(db.Integer, db.ForeignKey("siteinformation.id"))

    comments = db.Column(db.Text())
    datetime = db.Column(db.DateTime)