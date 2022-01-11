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

# from .. import spec
from flask import Blueprint

api = Blueprint("api", __name__)

# Import API endpoints here.

from ..auth.api import *
from ..misc.api import *
from ..document.api import *
from ..donor.api import *
from ..consent.api import *
from ..protocol.api import *
from ..attribute.api import *
from ..sample.api import *
from ..tmpstore.api import *
from ..storage.api import *
from ..procedure.api import *
from ..disease.api import *
from ..admin.api import *
from .responses import *
from .filters import *


def prepare_for_chart_js(a):
    ye = {"labels": [], "data": []}

    for (label, data) in a:
        ye["labels"].append(label)
        ye["data"].append(data)

    return ye


"""
@api.route("/")
def api_doc():
    return spec.to_dict()
"""
