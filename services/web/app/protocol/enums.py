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
    ALD = "Sample Aliquoting / Derivation"
    STR = "Sample Transfer"
    SDE = "Sample Destruction"

class FluidLongTermStorage(FormEnum):
    A = "PP tube 0.5-2mL @ -85 to -60°C"
    B = "PP tube 0.5-2mL @ -35 to -18°C"
    V = "PP tube 0.5-2mL @ < 135°C"
    C = "Cryotube 1-2mL in Liquid Nitrogen"
    D = "Cryotube 1-2mL @ -85 to -60°C"
    E = "Cryotube 1-2mL @ < 135°C"
    F = "Plastic cryo straw in Liquid Nitrogen"
    G = "Straw @ -85 to -60°C"
    H = "Straw @ -35 to -18°C"
    I = "Straw @ < -135°C"
    J = "PP tube > 5mL @ -85 to -60°C"
    K = "PP tube > 5mL @ -35 to -18°C"
    L = "Microplate @ -85 to -60°C"
    M = "Microplate @ -35 to -18°C"
    N = "Cryotube 1-2mL in Liquid Nitrogen"
    O = "Plastic cryo straw in Liquid Nitrogen"
    P = "Paraffin block @ Room Temp or 2 - 10°C"
    Q = "Bag in Liquid Nitrogen"
    R = "Dry technology medium @ Room Temp"
    S = "PP tube 40-500 @ -85 to -60°C"
    T = "PP tube 40-500 @ -35 to -18°C"
    W = "PP tube 40-500μL @ < 135°C"
    Y = "Original Container @ -85 to -18°C"
    X = "Unknown"
    Z = "Other"
