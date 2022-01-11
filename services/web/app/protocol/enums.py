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

from ..FormEnum import FormEnum


class ProtocolTextType(FormEnum):
    MATE = "Materials and Reagents"
    EQUP = "Equipment"
    SOFT = "Software"
    PROC = "Procedure"
    RECP = "Recipes"
    ANAL = "Data Analysis"


class ProtocolType(FormEnum):
    ASS = "Experimental Assay"
    ACQ = "Sample Acquisition"
    SAP = "Sample Processing"
    ALD = "Sample Aliquot / Derivation"
    STR = "Sample Transfer"
    SDE = "Sample Destruction"
    COL = "Collection"
    STU = "Study"
    TMP = "Temporary Storage"
