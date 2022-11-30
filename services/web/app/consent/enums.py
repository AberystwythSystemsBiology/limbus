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


class QuestionType(FormEnum):
    STND = "Standard"
    ELEC = "Electronic Storage"
    GENE = "Genetic Tests"
    FUTU = "Future Samples"
    EXTE = "Available for External Sources"
    COMM = "Commercial Restriction"
    ANIM = "Animal Work"
    OEUR = "Outside EU Access Restriction"
    XENO = "Xenograph Restriction"
    FUTR = "Future Research"
