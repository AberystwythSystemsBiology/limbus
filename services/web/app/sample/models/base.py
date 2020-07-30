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

from app import db
from ..enums import *


class Sample(db.Model):
    __tablename__ = "samples"

    id = db.Column(db.Integer, primary_key=True)
    # UUID4 length = 36
    uuid = db.Column(db.String(36))
    biobank_barcode = db.Column(db.String)

    sample_type = db.Column(db.Enum(SampleType))
    collection_date = db.Column(db.DateTime)
    sample_status = db.Column(db.Enum(SampleStatus))

    quantity = db.Column(db.Float)
    current_quantity = db.Column(db.Float)

    is_closed = db.Column(db.Boolean)

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))


class SampleDisposalInformation(db.Model):
    __tablename__ = "sample_disposal_instruction"
    id = db.Column(db.Integer, primary_key=True)

    disposal_instruction = db.Column(db.Enum(DisposalInstruction))
    disposal_date = db.Column(db.DateTime, nullable=True)

    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))


class SampleToDonor(db.Model):
    __tablename__ = "sample_to_donors"
    id = db.Column(db.Integer, primary_key=True)

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )

    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))
    donor_id = db.Column(db.Integer, db.ForeignKey("donors.id"))

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
