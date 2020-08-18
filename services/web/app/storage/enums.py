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


class EntityToStorageTpye(FormEnum):
    STB = "Sample to Box"
    STS = "Sample to Shelf"
    BTS = "Box to Shelf"


class FixedColdStorageType(FormEnum):
    FRI = "Fridge"
    FRE = "Freezer"


class FixedColdStorageTemps(FormEnum):
    L = "-150 to -86°C"
    A = "-85 to -60°C"
    B = "-59 to -35°C"
    C = "-34 to -18°C"
    D = "-17 to -10°C"
    E = "-9 to -5°C"
    F = "-4 to 0°C"
