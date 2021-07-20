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

from ...extensions import ma
import marshmallow_sqlalchemy as masql
from marshmallow import fields, ValidationError
from marshmallow_enum import EnumField
from ...database import ColdStorageShelf, EntityToStorage, SampleRack, Container, FixationType
from ...storage.enums import EntityToStorageType

import typing



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


class BasicSampleRackSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleRack

    id = masql.auto_field()
    serial_number = masql.auto_field()

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("storage.view_rack", id="<id>", _external=True),
        }
    )


class BasicColdStorageShelfSchema(masql.SQLAlchemySchema):
    class Meta:
        model = ColdStorageShelf

    id = masql.auto_field()
    name = masql.auto_field()

    storage_id = masql.auto_field()

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("storage.view_shelf", id="<id>", _external=True),
        }
    )


class EntityToStorageSchema(masql.SQLAlchemySchema):
    class Meta:
        model = EntityToStorage

    id = masql.auto_field()
    storage_type = EnumField(EntityToStorageType)

    rack = ma.Nested(BasicSampleRackSchema, many=False)
    shelf = ma.Nested(BasicColdStorageShelfSchema, many=False)
