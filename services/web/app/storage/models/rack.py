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

from ...sample.enums import Colour

class SampleRack(Base, UniqueIdentifierMixin, RefAuthorMixin, RefEditorMixin):
    serial_number = db.Column(db.String(256))
    description = db.Column(db.Text)
    colour = db.Column(db.Enum(Colour))
    num_rows = db.Column(db.Integer)
    num_cols = db.Column(db.Integer)