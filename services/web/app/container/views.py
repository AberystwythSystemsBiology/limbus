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

from ..extensions import ma
from ..database import (
    GeneralContainer,
    Container
)
from marshmallow_enum import EnumField
import marshmallow_sqlalchemy as masql
from .enums import ContainerUsedFor

from ..sample.enums import Colour
from ..auth.views import BasicUserAccountSchema


class NewContainerSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Container


class NewGeneralContainerSchema(masql.SQLAlchemySchema):
    class Meta:
        model = GeneralContainer

    name = masql.auto_field()
    manufacturer = masql.auto_field()
    description = masql.auto_field()
    colour = EnumField(Colour)
    used_for = EnumField(ContainerUsedFor)
    temperature = masql.auto_field()

new_general_container_schema = NewGeneralContainerSchema()
new_general_containers_schema = NewContainerSchema(many=True)

class GeneralContainerSchema(masql.SQLAlchemySchema):
    class Meta:
        model = GeneralContainer

    name = masql.auto_field()
    manufacturer = masql.auto_field()
    description = masql.auto_field()
    colour = EnumField(Colour)
    used_for = EnumField(ContainerUsedFor)
    temperature = masql.auto_field()