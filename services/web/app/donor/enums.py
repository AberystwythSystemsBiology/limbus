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


class Condition(FormEnum):
    UND = "Undetermined"
    GOO = "Good"
    FAI = "Fair"
    CRI = "Critical"


class CancerStage(FormEnum):
    NA = "Not-applicable"
    S0 = "Stage 0"
    S1 = "Stage 1"
    S2 = "Stage 2"
    S3 = "Stage 3"
    S4 = "Stage 4"


class RaceTypes(FormEnum):
    A = "White"
    A1 = "Welsh/English/Scottish/Northern Irish/British"
    A2 = "Irish"
    A3 = "Gypsy or Irish Traveller"
    A4 = "Any Other White Background"
    B = "Mixed/Multiple Ethnic Groups"
    B1 = "White and Black Caribbean"
    B2 = "White and Black African"
    B3 = "White and Asian"
    B4 = "Any Other Mixed/Multiple Ethnic Background"
    C = "Asian/Asian British"
    C1 = "Indian"
    C2 = "Pakistani"
    C3 = "Bangladeshi"
    C4 = "Chinese"
    C5 = "Any Other Asian Background"
    D = "Black"
    D1 = "African"
    D2 = "Caribbean"
    D3 = "Any Other Black/African/Carbibean Background"
    E = "Other Ethnic Group"
    E1 = "Arab"
    E2 = "Any Other Ethnic Group"
    UNK = "Unknown"


class BiologicalSexTypes(FormEnum):
    M = "Male"
    F = "Female"
    UNK = "Unknown"


class DonorStatusTypes(FormEnum):
    AL = "Alive"
    DE = "Deceased"
    UNK = "Unknown"
