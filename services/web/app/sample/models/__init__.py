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
    SampleSource,
)


class Sample(Base, RefAuthorMixin, RefEditorMixin):

    # TODO: Automated population.
    uuid = db.Column(db.String(36))

    barcode = db.Column(db.Text)

    source = db.Column(db.Enum(SampleSource))

    type = db.Column(db.Enum(SampleType))
    status = db.Column(db.Enum(SampleStatus))
    colour = db.Column(db.Enum(Colour))
    quantity = db.Column(db.Float)
    remaining_quantity = db.Column(db.Float)

    collection_event_id = db.Column(db.Integer, db.ForeignKey("sampleprotocolevent.id"))
    processing_event_id = db.Column(db.Integer, db.ForeignKey("sampleprotocolevent.id"))

    comments = db.Column(db.Text, nullable=True)

    site_id = db.Column(db.Integer, db.ForeignKey("siteinformation.id"))
    is_closed = db.Column(db.Boolean, default=False)

    '''
    parent = db.relationship(
        "Sample",
        secondary="subsampletosample",
        secondaryjoin="Sample.id==SubSampleToSample.subsample_id",
        uselist=False
    )

    children = db.relationship(
        "Sample",
        secondary="subsampletosample",
        secondaryjoin="Sample.id==SubSampleToSample.parent_id",
        uselist=True
    )
        '''

    disposal_information = db.relationship(
        "SampleDisposal",
        primaryjoin="SampleDisposal.sample_id==Sample.id",
        uselist=False
    )

    consent_information = db.relationship(
        "SampleConsent",
        uselist=False
    )

    documents = db.relationship("Document", secondary="sampledocument", uselist=True)
    reviews = db.relationship("SampleReview", uselist=True)

    # donor = db.relationship("Donor", uselist=False, secondary="sampletodonor")


class SampleDisposal(Base, RefAuthorMixin, RefEditorMixin):
    id = db.Column(db.Integer, primary_key=True)
    instruction = db.Column(db.Enum(DisposalInstruction))
    comments = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=True)
    sample_id = db.Column(db.Integer, db.ForeignKey("sample.id"))


"""
class SampleToDonor(Base, RefAuthorMixin, RefEditorMixin):
    __tablename__ = "sampletodonor"

    sample_id = db.Column(db.Integer, db.ForeignKey("sample.id"), unique=True)
    donor_id = db.Column(db.Integer, db.ForeignKey("donor.id"))
"""


class SubSampleToSample(Base, RefAuthorMixin, RefEditorMixin):

    parent_id = db.Column(db.Integer, db.ForeignKey("sample.id"))
    subsample_id = db.Column(db.Integer, db.ForeignKey("sample.id"))


from .protocol import *
from .attribute import *
from .types import *
from .consent import *
from .document import *
from .review import *
from .temp import *