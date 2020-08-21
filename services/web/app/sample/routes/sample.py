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

from .. import sample
import requests
from flask import render_template, url_for
from flask_login import login_required

import requests
from ...misc import get_internal_api_header

@sample.route("view/<uuid>", methods=["GET"])
@login_required
def view(uuid: str):
    return render_template("sample/view.html", uuid=uuid)

@sample.route("view/<uuid>/data", methods=["GET"])
@login_required
def view_data(uuid: str):
    sample_response = requests.get(
        url_for("api.sample_view_sample", uuid=uuid, _external=True),
        headers=get_internal_api_header()
    )

    if sample_response.status_code == 200:
        return sample_response.json()
    return sample_response.content

@sample.route("view/<uuid>/barcode/<t>")
@login_required
def view_barcode(uuid: str, t: str):
    barcode_response = requests.get(
        url_for("api.misc_generate_barcode", t=t, i=uuid, _external=True),
        headers=get_internal_api_header()
    )

    return barcode_response.content
    