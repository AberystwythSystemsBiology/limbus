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
from ...database import Sample

import marshmallow_sqlalchemy as masql

class SampleUUIDSchema(masql.SQLAlchemySchema):
    class Meta:
        model = Sample

    uuid = masql.auto_field(required=False)

    _links = ma.Hyperlinks(
        {"self": ma.URLFor("sample.view", uuid="<uuid>", _external=True)}
    )



from .filter import *
from .consent import *
from .disposal import *
from .document import *
from .filter import *
from .protocol import *
from .review import *
from .type import *
from .sample import *