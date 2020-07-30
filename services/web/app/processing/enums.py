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


class ProtocolSampleType(FormEnum):
    # Ideally I'd like to extend sample.enums.SampleType directly
    # to add the all, but it turns out that you can't
    # subclass an enumeration if an enumeration defines
    # any members. I love you Python, but sometimes I want
    # to strangle you.
    ALL = "All"
    FLU = "Fluid"
    CEL = "Cell"
    MOL = "Molecular"


class ProtocolTypes(FormEnum):
    ACQ = "Sample Acquisition"
    ALD = "Sample Aliquoting / Derivation"
    STR = "Sample Transfer"
    SDE = "Sample Destruction"


class ProtocolUploadTypes(FormEnum):
    # TODO: Extend this.
    # DOC = "Document"
    DIG = "Digital"
    # DIC = "Digital and Document"


# Replace this with something smarter.
# Something like Room Temp - 2 to 10*C - 35 to 38 C etc...
class ProcessingTemps(FormEnum):
    A = "Room Temperature"
    B = "2 to 10°C"
    C = "-35 to -38°C"
    U = "Unknown"
    O = "Other"


class ProcessingTimes(FormEnum):
    A = "< 2 hours"
    B = "2 to 4 hours"
    C = "8 to 12 hours"
    D = "12 to 24 hours"
    E = "24 to 48 hours"
    F = "> 48 hours"
    U = "Unknown"
    O = "Other"


class CentrifugationTime(FormEnum):
    A = "10 to 15 minutes"
    B = "30 minutes"
    U = "Unknown"
    O = "Other"


class CentrifugationWeights(FormEnum):
    A = "< 3000g"
    B = "3000g to 6000g"
    C = "> 1000g"
    U = "Unknown"
    O = "Other"


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
