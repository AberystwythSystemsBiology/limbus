# Copyright (C) 2020  Keiron O'Shea <keo7@aber.ac.uk>
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
    SampleBaseType,
    SampleStatus,
    DisposalInstruction,
    Colour,
    SampleSource,
    SampleStorageRequirement,
    BiohazardLevel,
)


class Sample(Base, UniqueIdentifierMixin, RefAuthorMixin, RefEditorMixin):
    __versioned__ = {}

    colour = db.Column(db.Enum(Colour))
    barcode = db.Column(db.Text)
    biohazard_level = db.Column(db.Enum(BiohazardLevel))
    source = db.Column(db.Enum(SampleSource))

    base_type = db.Column(db.Enum(SampleBaseType))

    status = db.Column(db.Enum(SampleStatus))

    collection_event_id = db.Column(db.Integer, db.ForeignKey("sampleprotocolevent.id"))

    quantity = db.Column(db.Float, nullable=False)
    remaining_quantity = db.Column(db.Float, nullable=False)

    site_id = db.Column(db.Integer, db.ForeignKey("siteinformation.id"))
    consent_id = db.Column(db.Integer, db.ForeignKey("sampleconsent.id"), nullable=False)

    storage_requirement = db.Column(db.Enum(SampleStorageRequirement))

    is_closed = db.Column(db.Boolean, default=False)

    # Relationship Information

    sample_type_information = db.relationship("SampleToType")

    collection_event = db.relationship(
        "SampleProtocolEvent",
        uselist=False,
        primaryjoin="SampleProtocolEvent.id==Sample.collection_event_id",
    )

    
    # Procesing Events
    processing_events = db.relationship("SampleProtocolEvent", uselist=True)

    consent_information = db.relationship("SampleConsent", uselist=False)

    disposal_information = db.relationship("SampleDisposal", uselist=False)

    documents = db.relationship("Document", secondary="sampledocument", uselist=True)
    reviews = db.relationship("SampleReview", uselist=True)

    comments = db.relationship("SampleComments", uselist=True, primaryjoin="SampleComments.sample_id==Sample.id")

    subsamples = db.relationship(
        "Sample",
        secondary="subsampletosample",
        primaryjoin="Sample.id==SubSampleToSample.parent_id",
        secondaryjoin="Sample.id==SubSampleToSample.subsample_id",
    )

    parent = db.relationship(
        "Sample",
        secondary="subsampletosample",
        primaryjoin="Sample.id==SubSampleToSample.subsample_id",
        secondaryjoin="Sample.id==SubSampleToSample.parent_id",
        uselist=False,
    )

    storage = db.relationship("EntityToStorage", uselist=True)

    donor = db.relationship(
        "Donor",
        secondary="donortosample",
        primaryjoin="Sample.id==DonorToSample.sample_id",
        secondaryjoin="Donor.id==DonorToSample.donor_id",
        uselist=False
    )

class SampleComments(Base, RefAuthorMixin, RefEditorMixin):
    __versioned__ = {}
    comments = db.Column(db.Text)
    sample_id = db.Column(db.Integer, db.ForeignKey("sample.id"))


class SubSampleToSample(Base, RefAuthorMixin, RefEditorMixin):
    __versioned__ = {}
    parent_id = db.Column(db.Integer, db.ForeignKey("sample.id"), primary_key=True)
    subsample_id = db.Column(db.Integer, db.ForeignKey("sample.id"), unique=True, primary_key=True)

class SampleDisposalProtocol(Base, RefAuthorMixin, RefEditorMixin):
    __versioned__ = {}
    instruction = db.Column(db.Enum(DisposalInstruction))
    comments = db.Column(db.Text)
    disposal_date = db.Column(db.Date, nullable=True)
    sample_id = db.Column(db.Integer, db.ForeignKey("sample.id"), unique=True, primary_key=True)
