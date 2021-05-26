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

from ...database import UserCart
from ...extensions import ma
import marshmallow_sqlalchemy as masql
from marshmallow_enum import EnumField

from ..views import BasicSampleSchema
from ...auth.views import BasicUserAccountSchema

class UserCartSampleSchema(masql.SQLAlchemySchema):
    class Meta:
        model = UserCart

    sample = ma.Nested(BasicSampleSchema, many=False)
    author = ma.Nested(BasicUserAccountSchema, many=False)
    created_on = ma.Date()

user_cart_samples_schema = UserCartSampleSchema(many=True)