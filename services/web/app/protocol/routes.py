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
    render_template,
    url_for
)

from flask_login import login_required

from . import protocol

from ..misc import get_internal_api_header
import requests

from .forms import ProtocolCreationForm

@login_required
@protocol.route("/")
def index():
    response = requests.get(
        url_for("api.protocol_home", _external=True), headers=get_internal_api_header()
    )

    if response.status_code == 200:
        return render_template(
            "protocol/index.html", protocols=response.json()["content"]
        )
    else:
        return response.content

@login_required
@protocol.route("/new", methods=["GET", "POST"])
def new():
    form = ProtocolCreationForm()
    if form.validate_on_submit():
        pass

    return render_template("protocol/new.html", form=form)