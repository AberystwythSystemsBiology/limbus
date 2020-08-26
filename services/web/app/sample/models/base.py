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


def generate_uuid() -> str:
    return str(uuid.uuid4())

class Sample(Base, RefAuthorMixin, RefEditorMixin):

    uuid = db.Column(db.String(36), default=generate_uuid, nullable=False, unique=True)

    barcode = db.Column(db.Text)

    source = db.Column(db.Enum(SampleSource))

    status = db.Column(db.Enum(SampleStatus))
    colour = db.Column(db.Enum(Colour))

    biohazard_level = db.Column(db.Enum(BiohazardLevel))

    comments = db.Column(db.Text, nullable=True)

    quantity = db.Column(db.Float, nullable=False)
    remaining_quantity = db.Column(db.Float, nullable=False)

    site_id = db.Column(db.Integer, db.ForeignKey("siteinformation.id"))

    # Type and container information
    type = db.Column(db.Enum(SampleType))
    # TODO
    sample_to_type_id = db.Column(db.Integer, db.ForeignKey("sampletotype.id"))
    sample_type_information = db.relationship("SampleToType")


    # Collection Informaiton
    # Done -> sample_new_sample_protocol_event
    collection_event_id = db.Column(db.Integer, db.ForeignKey("sampleprotocolevent.id")) 
    collection_information = db.relationship(
        "SampleProtocolEvent",
        uselist=False,
        primaryjoin="SampleProtocolEvent.id==Sample.collection_event_id",
    )

    # Consent Information
    # Done -> sample_new_sample_consent
    consent_id = db.Column(db.Integer, db.ForeignKey("sampleconsent.id"), nullable=False)
    consent_information = db.relationship(
        "SampleConsent",
        uselist=False
    )
    
    # Disposal Information
    # Done -> sample_new_disposal_instructions
    disposal_id = db.Column(
        db.Integer, db.ForeignKey("sampledisposal.id")
    )
    disposal_information = db.relationship(
        "SampleDisposal",
        uselist=False
    )

    # Processing Information
    # Done -> sample_new_sample_protocol_event
    processing_event_id = db.Column(db.Integer, db.ForeignKey("sampleprotocolevent.id"))
    processing_information = db.relationship(
        "SampleProtocolEvent",
        primaryjoin="SampleProtocolEvent.id==Sample.processing_event_id",
    )

    documents = db.relationship("Document", secondary="sampledocument", uselist=True)
    reviews = db.relationship("SampleReview", uselist=True)

    is_closed = db.Column(db.Boolean, default=False)

    subsamples = db.relationship(
        "Sample",
        secondary="subsampletosample",
        primaryjoin="Sample.id==SubSampleToSample.parent_id",
        secondaryjoin="Sample.id==SubSampleToSample.subsample_id"
    )


    parent = db.relationship(
        "Sample",
        secondary="subsampletosample",
        primaryjoin="Sample.id==SubSampleToSample.subsample_id",
        secondaryjoin="Sample.id==SubSampleToSample.parent_id",
        uselist=False
    )



    # donor = db.relationship("Donor", uselist=False, secondary="sampletodonor")


class SubSampleToSample(Base, RefAuthorMixin, RefEditorMixin):
    parent_id = db.Column(db.Integer, db.ForeignKey("sample.id"), primary_key=True)
    subsample_id = db.Column(db.Integer, db.ForeignKey("sample.id"), unique=True, primary_key=True)



class SampleDisposal(Base, RefAuthorMixin, RefEditorMixin):
    instruction = db.Column(db.Enum(DisposalInstruction))
    comments = db.Column(db.Text)
    disposal_date = db.Column(db.Date, nullable=True)
