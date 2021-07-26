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
    Container,
    ContainerFixationType,
)

from marshmallow_enum import EnumField
import marshmallow_sqlalchemy as masql
from .enums import ContainerUsedFor

from ..sample.enums import Colour
from ..auth.views import BasicUserAccountSchema


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
new_general_containers_schema = NewGeneralContainerSchema(many=True)


class GeneralContainerSchema(masql.SQLAlchemySchema):
    class Meta:
        model = GeneralContainer

    id = masql.auto_field()
    name = masql.auto_field()
    manufacturer = masql.auto_field()
    description = masql.auto_field()
    colour = EnumField(Colour)
    used_for = EnumField(ContainerUsedFor, by_value=True)
    temperature = masql.auto_field()
    author = ma.Nested(BasicUserAccountSchema)


general_container_schema = GeneralContainerSchema()
general_containers_schema = GeneralContainerSchema(many=True)


class NewContainerSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Container

    cellular = masql.auto_field()
    fluid = masql.auto_field()
    tissue = masql.auto_field()
    container = ma.Nested(NewGeneralContainerSchema)
    sample_rack = masql.auto_field()


new_container_schema = NewContainerSchema()




class ContainerSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Container

    id = masql.auto_field()
    is_locked = masql.auto_field()
    cellular = masql.auto_field()
    fluid = masql.auto_field()
    tissue = masql.auto_field()
    sample_rack = masql.auto_field()
    author = ma.Nested(BasicUserAccountSchema)
    container = ma.Nested(GeneralContainerSchema)
    created_on = ma.Date()

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor(
                "container.view_container", id="<id>", _external=True
            ),
            "edit": ma.URLFor(
                "container.edit_container", id="<id>", _external=True
            )
        }
    )


container_schema = ContainerSchema()
containers_schema = ContainerSchema(many=True)


class ContainerFixationTypeSchema(masql.SQLAlchemySchema):
    class Meta:
        model = ContainerFixationType

    id = masql.auto_field()
    is_locked = masql.auto_field()
    formulation = masql.auto_field()
    start_hour = masql.auto_field()
    end_hour = masql.auto_field()
    created_on = ma.Date()
    container = ma.Nested(GeneralContainerSchema)
    author = ma.Nested(BasicUserAccountSchema)

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor(
                "container.view_fixation_type", id="<id>", _external=True
            ),
            "edit": ma.URLFor(
                "container.edit_fixation_type", id="<id>", _external=True
            )
        }
    )


container_fixation_type_schema = ContainerFixationTypeSchema()
container_fixation_types_schema = ContainerFixationTypeSchema(many=True)


class NewContainerFixationTypeSchema(masql.SQLAlchemySchema):
    class Meta:
        model = ContainerFixationType

    container = ma.Nested(NewGeneralContainerSchema)
    formulation = masql.auto_field()
    start_hour = masql.auto_field()
    end_hour = masql.auto_field()


new_container_fixation_type_schema = NewContainerFixationTypeSchema()

