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
from flask import render_template, url_for, flash, redirect, abort
from flask_login import login_required
import requests
from ...misc import get_internal_api_header
from ..forms import ProtocolEventForm
from datetime import datetime


@sample.route("<uuid>/protocol_event/new", methods=["GET", "POST"])
@login_required
def new_protocol_event(uuid):
    sample_response = requests.get(
        url_for("api.sample_view_sample", uuid=uuid, _external=True),
        headers=get_internal_api_header(),
    )

    if sample_response.status_code == 200:

        protocols_response = requests.get(
            url_for("api.protocol_query", _external=True),
            headers=get_internal_api_header(),
            json={"is_locked": False},
        )

        protocols = []

        if protocols_response.status_code == 200:
            for protocol in protocols_response.json()["content"]:
                protocols.append(
                    (
                        int(protocol["id"]),
                        "LIMBPRO-%s: %s" % (protocol["id"], protocol["name"]),
                    )
                )

        form = ProtocolEventForm(protocols)

        if form.validate_on_submit():
            new_event = requests.post(
                url_for("api.sample_new_sample_protocol_event", _external=True),
                headers=get_internal_api_header(),
                json={
                    "event": {
                        "datetime": str(
                            datetime.strptime(
                                "%s %s" % (form.date.data, form.time.data),
                                "%Y-%m-%d %H:%M:%S",
                            )
                        ),
                        "undertaken_by": form.undertaken_by.data,
                        "comments": form.comments.data,
                    },
                    "protocol_id": form.protocol_id.data,
                    "sample_id": sample_response.json()["content"]["id"],
                },
            )

            if new_event.status_code == 200:
                flash("Protocol Event Successfully Added!")
                return redirect(url_for("sample.view", uuid=uuid))
            flash("We have a problem!")
        return render_template(
            "sample/protocol/new.html",
            form=form,
            sample=sample_response.json()["content"],
        )


@sample.route("/protocol_event/<uuid>/edit", methods=["GET", "POST"])
@login_required
def edit_protocol_event(uuid):
    form = ProtocolEventForm([])
    abort(501)


@sample.route("/protocol_event/<uuid>/remove", methods=["GET", "POST"])
@login_required
def remove_protocol_event(uuid):
    print("About to remove")
    remove_response = requests.post(
        url_for("api.sample_remove_sample_protocol_event", uuid=uuid, _external=True),
        headers=get_internal_api_header(),
    )

    if remove_response.status_code == 200:
        flash("Protocol Event Successfully Deleted!")
        sample_uuid = remove_response.json()["content"]
        return redirect(url_for("sample.view", uuid=sample_uuid))
    else:
        flash("We have a problem: %s" % (remove_response.json()))
        abort(501)
