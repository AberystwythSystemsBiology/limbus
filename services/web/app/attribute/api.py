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

from ..api import api
from ..api.responses import *
from ..decorators import token_required

from flask import request, current_app
from marshmallow import ValidationError

from ..auth.models import UserAccount
from .models import Attribute
from .views import (
    basic_attributes_schema,
)

@api.route("/attribute")
@token_required
def attribute_home(tokenuser: UserAccount):
    return success_with_content_response(
        basic_attributes_schema.dumps(Attribute.query.all())
    )

@api.route("/attribute/new", methods=["POST"])
@token_required
def attribute_new_attribute(tokenuser: UserAccount):
    pass