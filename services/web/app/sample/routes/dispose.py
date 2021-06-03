# Copyright (C) 2021  Keiron O'Shea <keo7@aber.ac.uk>
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
from flask import render_template, url_for, flash, session, redirect, abort
from flask_login import login_required
from datetime import datetime

from ...misc import get_internal_api_header, flask_return_union
import requests

from uuid import uuid4

from ..forms import SampleDisposalEventForm


@sample.route("<uuid>/dispose", methods=["GET", "POST"])
@login_required
def dispose(uuid: str) -> flask_return_union:
    sample_response = requests.get(
        url_for("api.sample_view_sample", uuid=uuid, _external=True),
        headers=get_internal_api_header(),
    )

    if sample_response.status_code == 200:

        # Limit protocols response so that we only retrieve SDE (Sample Disposal)
        protocols_response = requests.get(
            url_for("api.protocol_query", _external=True),
            headers=get_internal_api_header(),
            json={"is_locked": False, "type": ["SDE", "STR"]},
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

        form = SampleDisposalEventForm(protocols)

        if form.validate_on_submit():

            # These to be done in a single API call.

            ## Create new Protocol Event: Done
            ## Create new Disposal Event
            ## Close Sample

            new_disposal_event_response = requests.post(
                url_for("api.sample_new_disposal_event", _external=True),
                headers=get_internal_api_header(),
                json={
                    "reason": form.reason.data,
                    "event" : {
                    "datetime": str(
                        datetime.strptime(
                            "%s %s" % (form.date.data, form.time.data),
                            "%Y-%m-%d %H:%M:%S",
                        )),
                        "comments": form.comments.data,
                        "undertaken_by": form.undertaken_by.data
                    },
                    "protocol_id": form.protocol_id.data,
                    "sample_uuid": sample_response.json()["content"]["uuid"],
                },
            )

            if new_disposal_event_response.status_code == 200:
                flash("Sample Disposed Successfully")
                return redirect("sample.index")

            else:
                return new_disposal_event_response.content

        return render_template(
            "sample/disposal/new.html",
            sample=sample_response.json()["content"],
            form=form,
        )
    else:
        abort(sample_response.status_code)
