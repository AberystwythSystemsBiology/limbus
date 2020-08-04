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
    url_for,
    flash,
    redirect,
)

from flask_login import login_required

from . import protocol

from ..misc import get_internal_api_header
import requests

from .forms import ProtocolCreationForm, MdeForm

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
        protocol_information = {
            "name": form.name.data,
            "doi": form.doi.data,
            "type": form.type.data
        }

        response = requests.post(
            url_for("api.protocol_new_protocol", _external=True),
            headers=get_internal_api_header(),
            json=protocol_information
        )

        if response.status_code == 200:
            flash("Protocol Successfully Created")
            return redirect(url_for("protocol.index"))
        else:
            flash("Error: %s - %s" % (response.status_code, response.json()))

    return render_template("protocol/new.html", form=form)

@protocol.route("/LIMBPRO-<id>")
@login_required
def view(id):
    return "Hello World"

@protocol.route("/LIMBPRO-<id>/add")
@login_required
def new_text(id):
    form = MdeForm()
    return render_template("protocol/new_text.html", form=form)