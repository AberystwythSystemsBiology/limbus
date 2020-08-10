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

from app import db, Base
from ...mixins import RefAuthorMixin, RefEditorMixin
from ..enums import SampleType, SampleStatus, DisposalInstruction


class Sample(Base, RefAuthorMixin, RefEditorMixin):
    __tablename__ = "sample"
    uuid = db.Column(db.String(36))
    barcode = db.Column(db.String)
    type = db.Column(db.Enum(SampleType))
    collection_date = db.Column(db.DateTime)
    status = db.Column(db.Enum(SampleStatus))
    quantity = db.Column(db.Float)
    current_quantity = db.Column(db.Float)
    is_closed = db.Column(db.Boolean)
    disposal_information = db.relationship("SampleDisposalInformation")


class SampleDisposalInformation(Base, RefAuthorMixin, RefEditorMixin):
    __tablename__ = "sampledisposalinstruction"
    id = db.Column(db.Integer, primary_key=True)
    instruction = db.Column(db.Enum(DisposalInstruction))
    comments = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=True)
    sample_id = db.Column(db.Integer, db.ForeignKey("sample.id"))


class SampleToDonor(Base, RefAuthorMixin, RefEditorMixin):
    __tablename__ = "sampletodonor"

    sample_id = db.Column(db.Integer, db.ForeignKey("sample.id"))
    donor_id = db.Column(db.Integer, db.ForeignKey("donor.id"))


from .processing import *
from .attribute import *
from .types import *
from .consent import *
from .document import *
from .aliquot import *
