# Copyright (C) 2020  Keiron O'Shea <keo7@aber.ac.uk>
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

from .. import admin
from ...decorators import check_if_admin
from ...misc import get_internal_api_header

from ...auth.forms import UserAccountRegistrationForm, UserAccountEditForm
from ..forms import AdminUserAccountEditForm
from ..forms.auth import AccountLockForm

from flask import render_template, url_for, redirect, abort, flash
from flask_login import current_user, login_required

import requests


@admin.route("/auth/", methods=["GET"])
@check_if_admin
@login_required
def auth_index():
    return render_template("admin/auth/index.html")


@admin.route("/auth/new", methods=["GET", "POST"])
@check_if_admin
@login_required
def auth_new_account():
    sites_response = requests.get(
        url_for("api.site_home", _external=True), headers=get_internal_api_header()
    )

    if sites_response.status_code == 200:
        sites = []

        for site in sites_response.json()["content"]:
            sites.append(
                [int(site["id"]), "LIMBSIT-%s: %s" % (site["id"], site["name"])]
            )

        form = UserAccountRegistrationForm(sites, with_type=True)

        if form.validate_on_submit():

            new_user_response = requests.post(
                url_for("api.auth_new_user", _external=True),
                json={
                    "title": form.title.data,
                    "first_name": form.first_name.data,
                    "middle_name": form.middle_name.data,
                    "last_name": form.last_name.data,
                    "email": form.email.data,
                    "account_type": form.type.data,
                    "password": form.password.data,
                    "site_id": form.site.data,
                },
                headers=get_internal_api_header(),
            )

            if new_user_response.status_code == 200:
                flash("User successfully added!")
                return redirect(url_for("admin.auth_index"))
            else:
                flash("We have encountered a problem :(")

        return render_template("/admin/auth/new.html", form=form)
    else:
        return abort(500)


@admin.route("/auth/<id>", methods=["GET", "POST"])
@check_if_admin
@login_required
def auth_view_account(id):
    response = requests.get(
        url_for("api.auth_view_user", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    if response.status_code == 200:
        form = AccountLockForm(response.json()["content"]["email"])

        if form.validate_on_submit():

            lock_response = requests.put(
                url_for("api.auth_lock_user", id=id, _external=True),
                headers=get_internal_api_header(),
            )

            if lock_response.status_code == 200:
                if lock_response.json()["content"]["is_locked"]:
                    flash("User Account locked!")
                else:
                    flash("User Account unLocked!")
                return redirect(url_for("admin.auth_index"))
            else:
                flash("We were unable to umllock the User Account.")

        return render_template(
            "admin/auth/view.html", user=response.json()["content"], form=form
        )
    else:
        return abort(response.status_code)


@admin.route("/auth/data", methods=["GET"])
@check_if_admin
@login_required
def auth_data():
    auth_response = requests.get(
        url_for("api.auth_home", _external=True),
        headers=get_internal_api_header(),
    )

    if auth_response.status_code == 200:
        return auth_response.json()
    return auth_response.content



@admin.route("/auth/<id>/edit", methods=["GET", "POST"])
@check_if_admin
@login_required
def admin_edit_account(id):
    # TODO
    response = requests.get(
        url_for("api.auth_view_user", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    sites_response = requests.get(
        url_for("api.site_home_tokenuser", _external=True), headers=get_internal_api_header()
    )
    sites=[0, None]
    if sites_response.status_code == 200:
        sites = sites_response.json()["content"]["choices"]
    else:
        flash("No site created!")
        return render_template(
            "admin/auth/edit.html", user=response.json()["content"], form=form
        )

    print("resps", response.text)
    account_data = response.json()["content"]
    account_data = {}

    for k in ["account_type", "email"]:
        account_data[k] = response.json()["content"][k]
        account_data.update({"site_id": response.json()["content"]["site"]["id"]})
        print("account_data", account_data)

    if response.status_code == 200:
        form = AdminUserAccountEditForm(account_data)
        #["email"])
        print(str(form.data))
        # form.data_entry.sites.choices = []
        # form.data_entry.consent_templates.choices = []
        # form.data_entry.stu_protocols.choices = []
        # form.data_entry.acq_protocols.choices = []
        if form.validate_on_submit():
            edit_response = requests.put(
                url_for("api.admin_edit_account", id=id, _external=True),
                headers=get_internal_api_header(),
            )

            if edit_response.status_code == 200:
                #flash("User account setting updated successfully!")
                flash("User account updated successfully!")
                return redirect(url_for("admin.auth_view_account", id=id))
            else:
                flash(edit_response.json()["message"])

        return render_template(
            "admin/auth/edit.html", user=response.json()["content"], form=form
        )
    else:
        return abort(response.status_code)
