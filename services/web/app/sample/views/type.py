# Copyright (C) 2020  Keiron O'Shea <keo7@aber.ac.uk>
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

import typing

from ...extensions import ma
from ...database import SampleToType, Container

from marshmallow_enum import EnumField
import marshmallow_sqlalchemy as masql

from marshmallow import fields, ValidationError

from ..enums import (
    FluidContainer,
    FluidSampleType,
    CellSampleType,
    TissueSampleType,
    FixationType,
    CellContainer,
    MolecularSampleType,
)

from ...auth.views import BasicUserAccountSchema

class UserCreatedContainer(fields.Field):
    """User Created Container that serialises and deserialises a Container."""

    def _deserialize(
        self,
        value: typing.Any,
        attr: typing.Optional[str],
        data: typing.Optional[typing.Mapping[str, typing.Any]],
        **kwargs
    ):

        container = Container.query.filter_by(id=value).first()

        if container is None:
            raise ValidationError("Not a valid container id")
        else:
            return int(value)

class UserCreatedFixationType(fields.Field):
    """User Created Container that serialises and deserialises a Container."""

    def _deserialize(
        self,
        value: typing.Any,
        attr: typing.Optional[str],
        data: typing.Optional[typing.Mapping[str, typing.Any]],
        **kwargs
    ):

        fixation = FixationType.query.filter_by(id=value).first()

        if fixation is None:
            raise fixation("Not a valid fixation id")
        else:
            return int(value)
class NewFluidSampleSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleToType

    fluid_sample_type = EnumField(FluidSampleType)
    fluid_container_id = UserCreatedContainer(required=True)


new_fluid_sample_schema = NewFluidSampleSchema()

class NewCellSampleSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleToType

    cellular_type = EnumField(CellSampleType)
    tissue_type = EnumField(TissueSampleType)
    cell_container_id = UserCreatedContainer(required=True)
    fixation_type_id = UserCreatedFixationType(required=True)

new_cell_sample_schema = NewCellSampleSchema()


class NewMolecularSampleSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleToType

    molecular_type = EnumField(MolecularSampleType)
    fluid_container_id = UserCreatedContainer(required=True)


new_molecular_sample_schema = NewMolecularSampleSchema()




class SampleTypeSchema(ma.SQLAlchemySchema):
    class Meta:
        model = SampleToType

    id = masql.auto_field()

    fluid_type = EnumField(FluidSampleType, by_value=True)
    molecular_type = EnumField(MolecularSampleType, by_value=True)
    cellular_type = EnumField(CellSampleType, by_value=True)
    tissue_type = EnumField(TissueSampleType, by_value=True)

    author = ma.Nested(BasicUserAccountSchema)


sample_type_schema = SampleTypeSchema()
