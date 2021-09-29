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
    sample_id = db.Column(db.Integer, db.ForeignKey("sample.id"))
    rack_id = db.Column(db.Integer, db.ForeignKey("samplerack.id"))
    storage_type = db.Column(db.Enum(CartSampleStorageType))
    selected = db.Column(db.Boolean, default=False)
    sample = db.relationship("Sample", viewonly=True)
    rack = db.relationship("SampleRack", viewonly=True)


class SampleShipment(Base, UniqueIdentifierMixin, RefAuthorMixin, RefEditorMixin):
    __versioned__ = {}

    site_id = db.Column(db.Integer, db.ForeignKey("siteinformation.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"))

    new_site = db.relationship("SiteInformation")
    event = db.relationship("Event")

    involved_samples = db.relationship(
        "SampleShipmentToSample",
        primaryjoin="SampleShipmentToSample.shipment_id == SampleShipment.id",
    )

    #shipment_status_id = db.Column(db.Integer, db.ForeignKey("SampleShipmentStatus.id"))
    shipment_status = db.relationship("SampleShipmentStatus", uselist=False)
    #    primaryjoin="SampleShipmentStatus.shipment_id == SampleShipment.id")#, uselist=False)

class SampleShipmentToSample(Base, RefAuthorMixin, RefEditorMixin):
    sample_id = db.Column(db.Integer, db.ForeignKey("sample.id"))
    from_site_id = db.Column(db.Integer, db.ForeignKey("siteinformation.id"))

    old_site = db.relationship("SiteInformation")
    sample = db.relationship("Sample")

    shipment_id = db.Column(db.Integer, db.ForeignKey("sampleshipment.id"))
    shipment = db.relationship("SampleShipment")

    #protocol_event_id = db.Column(db.Integer, db.ForeignKey("sampleprotocolevent.id"))


class SampleShipmentStatus(Base, RefAuthorMixin, RefEditorMixin):
    __versioned__ = {}

    status = db.Column(db.Enum(SampleShipmentStatusStatus))
    comments = db.Column(db.Text())
    tracking_number = db.Column(db.Text())
    datetime = db.Column(db.DateTime)
    shipment_id = db.Column(
        db.Integer, db.ForeignKey("sampleshipment.id"), nullable=False
    )
    shipment = db.relationship("SampleShipment", viewonly=True)
