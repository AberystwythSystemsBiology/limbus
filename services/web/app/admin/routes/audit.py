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

from .. import admin
from flask import json, render_template, url_for, flash, redirect, abort, request
from flask_login import login_required

import requests
from ...misc import get_internal_api_header

from ..forms import AuditFilterForm
from datetime import datetime
from ..enums import *


@admin.route("/audit/index", methods=["GET", "POST"])
@login_required
def audit_index():

    sites_response = requests.get(
        url_for("api.site_home_tokenuser", _external=True),
        headers=get_internal_api_header(),
    )

    sites = []
    if sites_response.status_code == 200:
        sites = sites_response.json()["content"]["choices"]
        # print("sites", sites)

    sites.append((99999, "Bots"))
    # users_by_site = {s[0]: [] for s in sites}
    sites_dict = {s[0]: s[1] for s in sites}

    auth_response = requests.get(
        url_for("api.auth_home_tokenuser", _external=True),
        headers=get_internal_api_header(),
    )

    users = []
    if auth_response.status_code == 200:
        auth_info = auth_response.json()["content"]
        print("auth_info", auth_info)
        for user in auth_info:
            if user["site_id"]:
                site_id = user["site_id"]
            else:
                site_id = 99999

            user_label = "|".join(
                [
                    user["email"],
                    user["account_type"],
                    user["first_name"] + " " + user["last_name"],
                ]
            )
            user_site_label = user_label + "[" + sites_dict[site_id] + "]"
            users.append((user["id"], user_site_label))
            # users_by_site[site_id].append((user["id"], user_label))

    form = AuditFilterForm(sites, users)
    return render_template(
        "admin/audit/index.html", form=form
    )  # , users_by_site=users_by_site)


@admin.route("/audit/query", methods=["POST"])
@login_required
def audit_query():
    args = request.json
    start_date = args.pop("start_date", datetime.today())
    end_date = args.pop("end_date", datetime.today())

    args["start_date"] = start_date
    args["end_date"] = end_date

    audit_response = requests.get(
        url_for("api.audit_query", _external=True),
        headers=get_internal_api_header(),
        json=args,
    )

    if audit_response.status_code != 200:
        flash(audit_response.json()["message"])
        # abort(audit_response.status_code)

    return audit_response.json()


@admin.route("/audit/sample/<uuid>", methods=["GET"])
@login_required
def audit_sample(uuid: str):
    audit_response = requests.get(
        url_for("api.audit_sample", uuid=uuid, _external=True),
        headers=get_internal_api_header(),
    )

    if audit_response.status_code != 200:
        abort(audit_response.status_code)

    return audit_response.json()
