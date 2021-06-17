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

from ...extensions import ma
from ...database import SampleToContainer
import marshmallow_sqlalchemy as masql
from marshmallow_enum import EnumField

from ..enums import SampleToContainerType

from ...auth.views import BasicUserAccountSchema

class SampleToContainerSchema(ma.SQLAlchemySchema):

    class Meta:
        model = SampleToContainer

    sample_id = masql.auto_field()
    container_id = masql.auto_field()
    fixation_type_id = masql.auto_field()
    type = EnumField(SampleToContainerType, by_value=True)
    author = ma.Nested(BasicUserAccountSchema)

sample_to_container_schema = SampleToContainerSchema()


class NewSampleToContainerSchema(ma.SQLAlchemySchema):
    class Meta:
        model = SampleToContainer

    sample_id = masql.auto_field()
    container_id = masql.auto_field()
    fixation_type_id = masql.auto_field()
    type = EnumField(SampleToContainerType)

new_sample_to_container_schema = NewSampleToContainerSchema()
