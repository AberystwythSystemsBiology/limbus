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

from flask import redirect, abort, render_template, url_for, session, flash, request, jsonify

from flask_login import current_user, login_required
import requests

from . import consent
from .. import db
from .forms import NewConsentFormTemplate

from .models import *
from ..misc import get_internal_api_header


@consent.route("/")
@login_required
def index():
    response = requests.get(
        url_for("api.consent_home", _external=True), headers=get_internal_api_header()
    )

    if response.status_code == 200:
        return render_template("consent/index.html", templates=response.json()["content"])
    else:
        return response.content


@consent.route("/LIMBPCF-<id>")
@login_required
def view(id):
    response = requests.get(
        url_for("api.consent_view_template", id=id, _external=True), headers=get_internal_api_header()
    )

    if response.status_code == 200:
        return render_template("consent/view.html", template=response.json()["content"])
    else:
        return response.content


@consent.route("/add", methods=["GET", "POST"])
@login_required
def new_template():
    form = NewConsentFormTemplate()
    if form.validate_on_submit():
        template_information = {
            "name": form.name.data,
            "description": form.description.data,
            "version": form.version.data
        }

        response = requests.post(
            url_for("api.consent_new_template", _external=True),
            headers=get_internal_api_header(),
            json=template_information
        )

        if response.status_code == 200:
            flash("Template Added Successfully")
            return redirect(url_for("consent.index"))
        else:
            return response.content

    return render_template("consent/new_template.html", form=form)

'''
form = UserAccountEditForm()

    if response.status_code == 200:
        if form.validate_on_submit():
            user_information = {
                "title": form.title.data,
                "first_name": form.first_name.data,
                "middle_name": form.middle_name.data,
                "last_name": form.last_name.data,
            }
            edit_response = requests.put(
                url_for("api.auth_edit_user", id=current_user.id, _external=True),
                headers=get_internal_api_header(),
                json=user_information,
            )
            if edit_response.status_code == 200:
                flash("User Edited")
                return redirect(url_for("auth.profile"))
            else:
                return edit_response.content

        form = UserAccountEditForm(data=response.json()["content"])
        return render_template("auth/edit.html", form=form)
    else:
        return abort(response.status_code)'''

@consent.route("/LIMBPCF-<id>/edit", methods=["GET", "POST"])
def edit_template(id):
    response = requests.get(
        url_for("api.consent_view_template", id=id, _external=True), headers=get_internal_api_header()
    )


    if response.status_code == 200:
        form = NewConsentFormTemplate()

        if form.validate_on_submit():

            consent_info = {
                "name": form.name.data,
                "description": form.description.data,
                "version": form.version.data
            }

            edit_response = requests.put(
                url_for("api.consent_edit_template", id=id, _external=True),
                headers=get_internal_api_header(),
                json=consent_info
            )

            if edit_response.status_code == 200:
                flash("Template Successfully Edited")
                return redirect(url_for("consent.view", id=id))
            else:
                return edit_response.content

        form = NewConsentFormTemplate(data=response.json()["content"])

        return render_template("consent/edit_template.html", form=form, template=response.json()["content"])

    else:
        return response.content