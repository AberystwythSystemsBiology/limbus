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

import marshmallow_sqlalchemy as masql
from marshmallow import fields

from ...extensions import ma
from ...database import Sample


class SampleFilterSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Sample

    uuid = masql.auto_field()
    barcode = masql.auto_field()
    colour = masql.auto_field()
    base_type = masql.auto_field()
    biohazard_level = masql.auto_field()
    source = masql.auto_field()
    status = masql.auto_field()
    current_site_id = fields.String()
    sample_type = fields.String()
    protocol_id = fields.Int()

    source_study = fields.Int()

    consent_status = fields.String()
    consent_type = fields.String()
