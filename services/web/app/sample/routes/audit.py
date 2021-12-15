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
from flask import json, render_template, url_for, flash, redirect, abort, request
from flask_login import login_required

import requests
from ...misc import get_internal_api_header

from ..forms import (
    SampleToDocumentAssociatationForm,
    SampleReviewForm,
    ProtocolEventForm,
    EditBasicForm
)

from ..enums import BiohazardLevel, Colour

from datetime import datetime

@sample.route("/<uuid>/audit", methods=["GET"])
@login_required
def audit(uuid: str):
    audit_response = requests.get(
        url_for("api.sample_audit", uuid=uuid, _external=True),
        headers=get_internal_api_header(),
    )

    if audit_response.status_code != 200:
        abort(audit_response.status_code)

    print(audit_response.text)
    #return audit_response.json()["content"]
    return render_template(
        "/tmpstore/view.html",
        hash=uuid,
        tmpstore=json.dumps(audit_response.json()["content"], indent=4),
    )

@sample.route("/audit/<start_date>/<end_date>", methods=["GET"])
@sample.route("/audit/<start_date>", methods=["GET"])
@login_required
def audit_by_period(start_date, end_date=None):
    audit_response = requests.get(
        url_for("api.sample_audit_period", start_date=start_date, end_date=end_date, _external=True),
        headers=get_internal_api_header(),
    )
    print("start:", start_date, " ; end:", end_date)
    if audit_response.status_code != 200:
        abort(audit_response.status_code)

    print(audit_response.text)
    #return audit_response.json()["content"]
    return render_template(
        "/tmpstore/view.html",
        hash="",
        tmpstore=json.dumps(audit_response.json()["content"], indent=4),
    )



@sample.route("/<uuid>/audit/protocol_event", methods=["GET"])
@login_required
def protocol_event_audit(uuid: str):
    audit_response = requests.get(
        url_for("api.protocol_event_audit", uuid=uuid, _external=True),
        headers=get_internal_api_header(),
    )

    if audit_response.status_code != 200:
        abort(audit_response.status_code)

    print(audit_response.text)
    #return audit_response.json()["content"]
    return render_template(
        "/tmpstore/view.html",
        hash=uuid,
        tmpstore=json.dumps(audit_response.json()["content"], indent=4),
    )