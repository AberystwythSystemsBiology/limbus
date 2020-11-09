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
from marshmallow import fields
from marshmallow_enum import EnumField
from ...database import Room

from ...auth.views import BasicUserAccountSchema


class BasicRoomSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Room
    id = masql.auto_field()
    name = masql.auto_field()


basic_room_schema = BasicRoomSchema()
basic_rooms_schema = BasicRoomSchema(many=True)


class RoomSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Room

    id = masql.auto_field()
    name = masql.auto_field()
    building = masql.auto_field()
    author = ma.Nested(BasicUserAccountSchema, many=False)


room_schema = RoomSchema()
rooms_schema = RoomSchema(many=True)


class NewRoomSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Room

    name = masql.auto_field()
    building_id = masql.auto_field()


new_room_schema = NewRoomSchema()
