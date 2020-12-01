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

from flask import (
    redirect,
    abort,
    render_template,
    url_for,
    session,
    request,
    jsonify,
    flash,
)

from flask_login import current_user, login_required
from .. import storage
import requests
from ...misc import get_internal_api_header


@storage.route("/site/LIMBSITE-<id>", methods=["GET"])
@login_required
def view_site(id):
    response = requests.get(
        url_for("api.site_view", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    if response.status_code == 200:
        return render_template(
            "storage/site/view.html", site=response.json()["content"]
        )

    return abort(response.status_code)
