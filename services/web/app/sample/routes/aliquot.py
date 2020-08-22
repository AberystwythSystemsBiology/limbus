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

from flask import render_template, redirect, session, url_for, request, abort
from flask_login import login_required, current_user
import requests


from ...database import db
from ..forms import SampleAliquotingForm
from ...misc import get_internal_api_header


@sample.route("view/<uuid>/aliquot", methods=["GET", "POST"])
@login_required
def aliquot(uuid: str):
    # An aliquot creates a specimen from the same type as the parent.

    protocol_response = requests.get(
        url_for("api.protocol_query", _external=True),
        headers=get_internal_api_header(),
        json={"is_locked": False},
    )

    if protocol_response.status_code != 200:
        abort(400)


    user_response = requests.get(
        url_for("api.auth_home", _external=True),
        headers=get_internal_api_header(),
        json={}
    )

    if user_response.status_code != 200:
        abort(400)

    processing_templates = protocol_response.json()["content"]
    users = user_response.json()["content"]

    form = SampleAliquotingForm(processing_templates, users)

    return render_template("sample/sample/aliquot/create.html", form=form)

@sample.route("view/<uuid>/derive")
@login_required
def derive(uuid: str):
    # A derivative creates a different specimen type from the parent.
    return "Hello World"