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
from flask import render_template, url_for, abort
from flask_login import login_required

from ...misc import get_internal_api_header

from ..forms import SampleFilterForm

import requests


@sample.route("/")
@login_required
def index() -> str:
    form = SampleFilterForm()

    return render_template("sample/index.html", form=form)


@sample.route("/query", methods=["POST"])
@login_required
def query_index():
    response = requests.get(
        url_for("api.sample_query", _external=True),
        headers=get_internal_api_header(),
        json=request.json,
    )

    if response.status_code == 200:
        return response.json()
    else:
        abort(response.status_code)


@sample.route("/export", methods=["POST"])
@login_required
def query_export():
    response = requests.get(
        url_for("api.sample_export", _external=True),
        headers=get_internal_api_header(),
        json=request.json,
    )

    if response.status_code == 200:
        return response.json()
    else:
        abort(response.status_code)


@sample.route("/biohazard_information")
@login_required
def biohazard_information() -> str:
    return render_template("sample/misc/biohazards.html")


from .add import *
from .protocol import *
from .sample import *
from .aliquot import *
from .review import *
from .attribute import *
from .dispose import *
from .shipment import *