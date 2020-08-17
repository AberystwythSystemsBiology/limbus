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
    BiohazardLevel,
)

import uuid

class Sample(Base, RefAuthorMixin, RefEditorMixin):

    uuid = db.Column(db.String(36), default=str(uuid.uuid4()), nullable=False)

    barcode = db.Column(db.Text)

    source = db.Column(db.Enum(SampleSource))

    type = db.Column(db.Enum(SampleType))
    status = db.Column(db.Enum(SampleStatus))
    colour = db.Column(db.Enum(Colour))

    biohazard_level = db.Column(db.Enum(BiohazardLevel))

    collection_event_id = db.Column(db.Integer, db.ForeignKey("sampleprotocolevent.id"))
    processing_event_id = db.Column(db.Integer, db.ForeignKey("sampleprotocolevent.id"))

    comments = db.Column(db.Text, nullable=True)

    site_id = db.Column(db.Integer, db.ForeignKey("siteinformation.id"))
    is_closed = db.Column(db.Boolean, default=False)

    disposal_information = db.relationship(
        "SampleDisposal",
        primaryjoin="SampleDisposal.sample_id==Sample.id",
        uselist=False
    )

    consent_id = db.Column(db.Integer, db.ForeignKey("sampleconsent.id"), nullable=False)

    consent_information = db.relationship(
        "SampleConsent",
        uselist=False,
        primaryjoin="SampleConsent.id==Sample.consent_id"
    )

    collection_information = db.relationship(
        "SampleProtocolEvent",
        uselist=False,
        primaryjoin="SampleProtocolEvent.id==Sample.collection_event_id"
    )

    processing_information = db.relationship(
        "SampleProtocolEvent",
        primaryjoin="SampleProtocolEvent.id==Sample.processing_event_id"
    )

    quantity = db.relationship("SampleQuantity", uselist=False)
    documents = db.relationship("Document", secondary="sampledocument", uselist=True)
    reviews = db.relationship("SampleReview", uselist=True)

    # donor = db.relationship("Donor", uselist=False, secondary="sampletodonor")

class SubSampleToSample(Base, RefAuthorMixin, RefEditorMixin):
    parent_id = db.Column(db.Integer, db.ForeignKey("sample.id"))
    subsample_id = db.Column(db.Integer, db.ForeignKey("sample.id"), unique=True)

    parent = db.relationship("Sample", primaryjoin="SubSampleToSample.parent_id==Sample.id", uselist=False)
    subsamples = db.relationship("Sample", primaryjoin="SubSampleToSample.subsample_id==Sample.id", uselist=True)

class SampleQuantity(Base, RefAuthorMixin, RefEditorMixin):
    quantity = db.Column(db.Float)
    remaining_quantity = db.Column(db.Float)
    sample_id = db.Column(db.Integer, db.ForeignKey("sample.id"), unique=True)


class SampleDisposal(Base, RefAuthorMixin, RefEditorMixin):

    sample_id = db.Column(db.Integer, db.ForeignKey("sample.id"), unique=True)
    instruction = db.Column(db.Enum(DisposalInstruction))
    comments = db.Column(db.Text)
    disposal_date = db.Column(db.DateTime, nullable=True)


"""
class SampleToDonor(Base, RefAuthorMixin, RefEditorMixin):
    __tablename__ = "sampletodonor"

    sample_id = db.Column(db.Integer, db.ForeignKey("sample.id"), unique=True)
    donor_id = db.Column(db.Integer, db.ForeignKey("donor.id"))
"""



from .protocol import *
from .attribute import *
from .types import *
from .consent import *
from .document import *
from .review import *
