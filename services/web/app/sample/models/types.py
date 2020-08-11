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

from ..enums import *


class SampleToFluidSampleType(Base, RefAuthorMixin, RefEditorMixin):
    __tablename__ = "sampletofluidsampletype"

    sample_id = db.Column(db.Integer, db.ForeignKey("sample.id"))
    type = db.Column(db.Enum(FluidSampleType))

class SampleToMolecularSampleType(Base, RefAuthorMixin, RefEditorMixin):
    __tablename__ = "sampletomolecularsampletype"

    sample_id = db.Column(db.Integer, db.ForeignKey("sample.id"))
    type = db.Column(db.Enum(MolecularSampleType))


class SampleToCellSampleType(Base, RefAuthorMixin, RefEditorMixin):
    __tablename__ = "sampletocellsampletype"

    sample_id = db.Column(db.Integer, db.ForeignKey("sample.id"))
    type = db.Column(db.Enum(CellSampleType))


class SampleToTissueSampleType(Base, RefAuthorMixin, RefEditorMixin):
    __tablename__ = "sampletotissuesampletype"

    sample_id = db.Column(db.Integer, db.ForeignKey("sample.id"))
    type = db.Column(db.Enum(TissueSampleType))
