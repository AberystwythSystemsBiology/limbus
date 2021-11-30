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
from ..enums import SampleShipmentStatusStatus, CartSampleStorageType


class UserCart(Base, RefAuthorMixin, RefEditorMixin):
    sample_id = db.Column(db.Integer, db.ForeignKey("sample.id", use_alter=True))
    rack_id = db.Column(db.Integer, db.ForeignKey("samplerack.id", use_alter=True))
    storage_type = db.Column(db.Enum(CartSampleStorageType))
    selected = db.Column(db.Boolean, default=False)
    sample = db.relationship("Sample")
    rack = db.relationship("SampleRack")


class SampleShipment(Base, UniqueIdentifierMixin, RefAuthorMixin, RefEditorMixin):
    __versioned__ = {}

    site_id = db.Column(db.Integer, db.ForeignKey("siteinformation.id", use_alter=True))
    address_id = db.Column(db.Integer, db.ForeignKey("address.id", use_alter=True))
    event_id = db.Column(db.Integer, db.ForeignKey("event.id", use_alter=True))

    new_site = db.relationship("SiteInformation")
    to_address = db.relationship("Address")
    event = db.relationship("Event", cascade="all, delete")

    involved_samples = db.relationship(
        "SampleShipmentToSample",
        primaryjoin="SampleShipmentToSample.shipment_id == SampleShipment.id",
        cascade = "all, delete"
    )

    shipment_status = db.relationship("SampleShipmentStatus", uselist=False)



class SampleShipmentToSample(Base, RefAuthorMixin, RefEditorMixin):
    __versioned__ = {}
    sample_id = db.Column(db.Integer, db.ForeignKey("sample.id", use_alter=True))
    from_site_id = db.Column(
        db.Integer, db.ForeignKey("siteinformation.id", use_alter=True)
    )

    old_site = db.relationship("SiteInformation")
    sample = db.relationship("Sample")

    shipment_id = db.Column(
        db.Integer, db.ForeignKey("sampleshipment.id", use_alter=True)
    )
    shipment = db.relationship("SampleShipment")

    protocol_event_id = db.Column(
        db.Integer, db.ForeignKey("sampleprotocolevent.id", use_alter=True)
    )

    transfer_protocol = db.relationship("SampleProtocolEvent", backref="shipment")

class SampleShipmentStatus(Base, RefAuthorMixin, RefEditorMixin):
    __versioned__ = {}

    status = db.Column(db.Enum(SampleShipmentStatusStatus))
    comments = db.Column(db.Text())
    courier = db.Column(db.String(128))
    tracking_number = db.Column(db.Text())
    datetime = db.Column(db.DateTime)
    shipment_id = db.Column(
        db.Integer, db.ForeignKey("sampleshipment.id", use_alter=True), nullable=False
    )
    shipment = db.relationship("SampleShipment")
