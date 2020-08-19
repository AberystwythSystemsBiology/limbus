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
from .base import *