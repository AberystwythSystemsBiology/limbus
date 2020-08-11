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
from ..enums import (
    SampleType,
    SampleStatus,
    DisposalInstruction,
    Colour,
    Source,
    Quality
)


class Sample(Base, RefAuthorMixin, RefEditorMixin):
    __tablename__ = "sample"
    # TODO: Automated population.
    uuid = db.Column(db.String(36))

    barcode = db.Column(db.Text)

    source = db.Column(db.Enum(Source))

    type = db.Column(db.Enum(SampleType))
    collection_date = db.Column(db.DateTime)
    status = db.Column(db.Enum(SampleStatus))
    colour = db.Column(db.Enum(Colour))
    quantity = db.Column(db.Float)
    remaining_quantity = db.Column(db.Float)

    comments = db.Column(db.Text, nullable=True)
    quality = db.Column(db.Enum(Quality))

    site_id = db.Column(db.Integer, db.ForeignKey("siteinformation.id"))
    is_closed = db.Column(db.Boolean, default=False)

    #donor = db.relationship("Donor", uselist=False, secondary="sampletodonor")



class SampleDisposal(Base, RefAuthorMixin, RefEditorMixin):
    __tablename__ = "sampledisposal"
    id = db.Column(db.Integer, primary_key=True)
    instruction = db.Column(db.Enum(DisposalInstruction))
    comments = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=True)
    sample_id = db.Column(db.Integer, db.ForeignKey("sample.id"))


'''
class SampleToDonor(Base, RefAuthorMixin, RefEditorMixin):
    __tablename__ = "sampletodonor"

    sample_id = db.Column(db.Integer, db.ForeignKey("sample.id"), unique=True)
    donor_id = db.Column(db.Integer, db.ForeignKey("donor.id"))
'''

class SubSampleToSample(Base, RefAuthorMixin, RefEditorMixin):
    __tablename__ = "subsampletosample"

    parent_id = db.Column(db.Integer, db.ForeignKey("sample.id"))
    subsample_id = db.Column(db.Integer, db.ForeignKey("sample.id"))


from .protocol import *
from .attribute import *
from .types import *
from .consent import *
from .document import *