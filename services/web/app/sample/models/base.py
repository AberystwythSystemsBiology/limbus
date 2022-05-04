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
    SampleBaseType,
    SampleStatus,
    DisposalInstruction,
    DisposalReason,
    Colour,
    SampleSource,
    BiohazardLevel,
    DisposalReason,
    AccessStatus,
)


class Sample(Base, UniqueIdentifierMixin, RefAuthorMixin, RefEditorMixin):
    __versioned__ = {}
    barcode = db.Column(db.Text)

    source = db.Column(db.Enum(SampleSource))

    status = db.Column(db.Enum(SampleStatus))
    colour = db.Column(db.Enum(Colour), nullable=True)

    biohazard_level = db.Column(db.Enum(BiohazardLevel))

    comments = db.Column(db.Text, nullable=True)

    quantity = db.Column(db.Float, nullable=False)
    remaining_quantity = db.Column(db.Float, nullable=False)

    site_id = db.Column(db.Integer, db.ForeignKey("siteinformation.id"))
    current_site_id = db.Column(db.Integer, db.ForeignKey("siteinformation.id"))
    access_status = db.Column(db.Enum(AccessStatus))

    base_type = db.Column(db.Enum(SampleBaseType))

    sample_to_type_id = db.Column(db.Integer, db.ForeignKey("sampletotype.id"))
    sample_type_information = db.relationship("SampleToType", cascade="all, delete")

    # Consent Information
    # Done -> sample_new_sample_consent
    consent_id = db.Column(
        db.Integer, db.ForeignKey("sampleconsent.id"), nullable=False
    )

    consent_information = db.relationship("SampleConsent", uselist=False)

    events = db.relationship("SampleProtocolEvent", uselist=True)
    subsample_event = db.relationship(
        "SampleProtocolEvent",
        uselist=False,
        secondary="subsampletosample",
        primaryjoin="Sample.id==SubSampleToSample.subsample_id",
        secondaryjoin="SampleProtocolEvent.id==SubSampleToSample.protocol_event_id",
        viewonly=True,
    )
    reviews = db.relationship("SampleReview", uselist=True, cascade="all, delete")
    shipments = db.relationship("SampleShipmentToSample", uselist=True)

    # Disposal Information
    # Done -> sample_new_disposal_instructions
    disposal_id = db.Column(db.Integer, db.ForeignKey("sampledisposal.id"))
    disposal_information = db.relationship(
        "SampleDisposal", foreign_keys=(disposal_id), uselist=False
    )

    documents = db.relationship("Document", secondary="sampledocument", uselist=True)

    is_closed = db.Column(db.Boolean, default=False)

    subsamples = db.relationship(
        "Sample",
        secondary="subsampletosample",
        primaryjoin="Sample.id==SubSampleToSample.parent_id",
        secondaryjoin="Sample.id==SubSampleToSample.subsample_id",
        viewonly=True,
    )

    parent = db.relationship(
        "Sample",
        secondary="subsampletosample",
        primaryjoin="Sample.id==SubSampleToSample.subsample_id",
        secondaryjoin="Sample.id==SubSampleToSample.parent_id",
        uselist=False,
        viewonly=True,
    )

    attributes = db.relationship(
        "AttributeData",
        secondary="sampletocustomattributedata",
        uselist=True,
        # cascade = "all, delete"
    )

    # storage = db.relationship("EntityToStorage", uselist=False, cascade="all, delete")
    storage = db.relationship(
        "EntityToStorage",
        primaryjoin="and_(EntityToStorage.sample_id == Sample.id, "
        "EntityToStorage.removed == False)",
        uselist=False,
    )  # , cascade="all, delete")

    donor = db.relationship("Donor", uselist=False, secondary="donortosample")


class SampleToEvent(Base, RefEditorMixin, RefAuthorMixin):
    sample_id = db.Column(db.Integer, db.ForeignKey("sample.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"))


class SubSampleToSample(Base, RefAuthorMixin, RefEditorMixin):
    __versioned__ = {}
    parent_id = db.Column(db.Integer, db.ForeignKey("sample.id"), primary_key=True)
    subsample_id = db.Column(
        db.Integer,
        db.ForeignKey("sample.id", use_alter=True),
        unique=True,
        primary_key=True,
    )
    protocol_event_id = db.Column(
        db.Integer,
        db.ForeignKey("sampleprotocolevent.id", use_alter=True),
        primary_key=True,
    )

    # protocol_event = db.relationship(
    #     "SampleProtocolEvent", uselist=False,
    #     foreign_keys=protocol_event_id,
    #     backref="subsamples_created"
    # )


class SampleDisposal(Base, RefAuthorMixin, RefEditorMixin):
    __versioned__ = {}

    sample_id = db.Column(db.ForeignKey("sample.id", use_alter=True))
    instruction = db.Column(db.Enum(DisposalInstruction))
    comments = db.Column(db.Text)
    disposal_date = db.Column(db.Date, nullable=True)
    review_event_id = db.Column(
        db.Integer, db.ForeignKey("samplereview.id", use_alter=True)
    )

    approved = db.Column(db.Boolean, nullable=True)
    approval_file_id = db.Column(
        db.Integer, db.ForeignKey("document.id", use_alter=True)
    )
    approval_file = db.relationship("Document")
    approval_event_id = db.Column(db.Integer, db.ForeignKey("event.id", use_alter=True))
    disposal_event_id = db.Column(
        db.Integer, db.ForeignKey("sampleprotocolevent.id", use_alter=True)
    )

    review_event = db.relationship("SampleReview", uselist=False)
    disposal_event = db.relationship(
        "SampleProtocolEvent",
        uselist=False,  # foreign_keys=disposal_event_id,
        # backref="disposal_instruction"
    )


class SampleDisposalEvent(Base, RefAuthorMixin, RefEditorMixin):
    __versioned__ = {}
    reason = db.Column(db.Enum(DisposalReason))
    sample_id = db.Column(
        db.Integer,
        db.ForeignKey("sample.id", use_alter=True),
        unique=True,
        primary_key=True,
    )
    protocol_event_id = db.Column(
        db.Integer, db.ForeignKey("sampleprotocolevent.id", use_alter=True)
    )
