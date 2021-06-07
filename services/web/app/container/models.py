# Copyright (C) 2021  Keiron O'Shea <keo7@aber.ac.uk>
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

from ..database import db, Base
from ..mixins import RefAuthorMixin, RefEditorMixin, UniqueIdentifierMixin
from ..sample.enums import Colour
from .enums import ContainerUsedFor


class GeneralContainer(Base, RefAuthorMixin, RefEditorMixin):
    name = db.Column(db.String(128))
    manufacturer = db.Column(db.String(128))
    description = db.Column(db.Text())
    colour = db.Column(db.Enum(Colour))
    used_for = db.Column(db.Enum(ContainerUsedFor))
    temperature = db.Column(db.Integer())


class ContainerFixationType(Base, UniqueIdentifierMixin, RefAuthorMixin, RefEditorMixin):
    general_container_id = db.Column(db.Integer, db.ForeignKey("generalcontainer.id"))


class Container(Base, UniqueIdentifierMixin, RefAuthorMixin, RefEditorMixin):

    general_container_id = db.Column(db.Integer, db.ForeignKey("generalcontainer.id"))

    cellular = db.Column(db.Boolean())
    fluid = db.Column(db.Boolean())
    tissue = db.Column(db.Boolean())

    sample_rack = db.Column(db.Boolean())

    container = db.relationship("GeneralContainer")