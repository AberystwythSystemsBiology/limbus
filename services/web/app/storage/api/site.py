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

from ...api import api
from ...api.responses import *

from flask import request, send_file
from ...decorators import token_required
from marshmallow import ValidationError

from ...database import SiteInformation, UserAccount

from ..views import (
    site_schema
)

@api.route("/misc/site/LIMBSIT-<id>", methods=["GET"])
@token_required
def site_view(id, tokenuser: UserAccount):
    return success_with_content_response(
        site_schema.dump(SiteInformation.query.filter_by(id=id).first_or_404())
    )