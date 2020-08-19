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
    FluidSampleType,
    MolecularSampleType,
    CellSampleType,
    TissueSampleType,
    CellContainer,
    FixationType,
)


class SampleToType(Base, RefAuthorMixin, RefEditorMixin):
    flui_type = db.Column(db.Enum(FluidSampleType), nullable=True)
    mole_type = db.Column(db.Enum(MolecularSampleType), nullable=True)
    cell_type = db.Column(db.Enum(CellSampleType), nullable=True)
    tiss_type = db.Column(db.Enum(TissueSampleType), nullable=True)


class SampleToContainer(Base, RefAuthorMixin, RefEditorMixin):
    flui_cont = db.Column(db.Enum(FluidSampleType), nullable=True)
    fixa_cont = db.Column(db.Enum(FixationType), nullable=True)
    cell_cont = db.Column(db.Enum(CellContainer), nullable=True)
