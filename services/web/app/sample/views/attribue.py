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


from ...extensions import ma
from ...database import SampleToCustomAttributeData

import marshmallow_sqlalchemy as masql

from ...auth.views import BasicUserAccountSchema


class NewSampleToCustomAttributeDataSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleToCustomAttributeData

    id = masql.auto_field()
    sample_id = masql.auto_field()
    attribute_data_id = masql.auto_field()

new_sample_to_custom_attribute_data_schema = NewSampleToCustomAttributeDataSchema()

class SampleToCustomAttributeDataSchema(masql.SQLAlchemySchema):
    class Meta:
        model = SampleToCustomAttributeData

    id = masql.auto_field()
    sample_id = masql.auto_field()
    attribute_data_id = masql.auto_field()

sample_to_custom_attribute_data_schema = SampleToCustomAttributeData()