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

from ..database import db, Base
from .enums import *
from ..sample.enums import Colour
from ..mixins import RefAuthorMixin, RefEditorMixin, UniqueIdentifierMixin


class Donor(Base, UniqueIdentifierMixin, RefAuthorMixin, RefEditorMixin):
    __versioned__ = {}
    dob = db.Column(db.Date)

    colour = db.Column(db.Enum(Colour))
    registration_date = db.Column(db.Date)
    mpn = db.Column(db.String(128))

    sex = db.Column(db.Enum(BiologicalSexTypes))
    diagnoses = db.relationship("DonorDiagnosisEvent")

    enrollment_site_id = db.Column(db.ForeignKey("siteinformation.id"))
    status = db.Column(db.Enum(DonorStatusTypes))
    death_date = db.Column(db.Date)
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    race = db.Column(db.Enum(RaceTypes))


class DonorToSample(Base, RefAuthorMixin, RefEditorMixin):
    sample_id = db.Column(db.Integer, db.ForeignKey("sample.id"))
    donor_id = db.Column(db.Integer, db.ForeignKey("donor.id"))


class DonorDiagnosisEvent(Base, RefAuthorMixin, RefEditorMixin):
    donor_id = db.Column(db.Integer, db.ForeignKey("donor.id"))

    doid_ref = db.Column(db.String())

    stage = db.Column(db.Enum(CancerStage))
    diagnosis_date = db.Column(db.Date)

    comments = db.Column(db.Text())
