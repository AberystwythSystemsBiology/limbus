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
from ..mixins import RefAuthorMixin, RefEditorMixin


class Donor(Base, RefAuthorMixin, RefEditorMixin):
    __versioned__ = {}
    uuid = db.Column(db.String(36))
    age = db.Column(db.Integer)
    sex = db.Column(db.Enum(BiologicalSexTypes))
    status = db.Column(db.Enum(DonorStatusTypes))
    death_date = db.Column(db.DateTime)

    weight = db.Column(db.Float)
    height = db.Column(db.Float)

    race = db.Column(db.Enum(RaceTypes))
