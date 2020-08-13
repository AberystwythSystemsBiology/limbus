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

from ..extensions import ma
from ..database import TemporaryStore

import marshmallow_sqlalchemy as masql
from marshmallow_enum import EnumField
from .enums import StoreType

from ..auth.views import BasicUserAccountSchema, UserAccountSearchSchema

class StoreSchema(masql.SQLAlchemySchema):
    class Meta:
        model = TemporaryStore

    uuid = masql.auto_field()
    data = masql.auto_field()
    author = ma.Nested(BasicUserAccountSchema)
    type = EnumField(StoreType)

store_schema = StoreSchema()
stores_schema = StoreSchema(many=True)

class NewStoreSchema(masql.SQLAlchemySchema):
    class Meta:
        model = TemporaryStore

    uuid = masql.auto_field()
    data = masql.auto_field()
    author_id = masql.auto_field()
    type = EnumField(StoreType)

new_store_schema = NewStoreSchema()

class StoreSearchSchema(masql.SQLAlchemySchema):
    class Meta:
        model = TemporaryStore

    uuid = masql.auto_field()
    data = masql.auto_field()
    author = ma.Nested(UserAccountSearchSchema)
    type = EnumField(StoreType)


class StoreUpdateSchema(masql.SQLAlchemySchema):
    class Meta:
        model = TemporaryStore

    data = masql.auto_field()

store_update_schema = StoreUpdateSchema()