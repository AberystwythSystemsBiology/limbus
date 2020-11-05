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

from . import donor
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from .models import Donor
from .forms import DonorCreationForm
from .views import DonorIndexView, DonorView

from .. import db

import uuid


@donor.route("/")
@login_required
def index():
    response = requests.get(
        url_for("api.donor_home", _external=True), headers=get_internal_api_header()
    )

    if response.status_code == 200:
        return render_template(
            "donor/index.html", template=response.json()["content"]
        )
    else:
        return abort(response.status_code)


@donor.route("/LIMBDON-<id>")
@login_required
def view(id):
    response = requests.get(
        url_for("api.donor_view", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    if response.status_code == 200:
        return render_template("donor/view.html", template=response.json()["content"])
    else:
        return response.content


@login_required
@donor.route("/new", methods=["GET", "POST"])
def add():
    form = DonorCreationForm()
    if form.validate_on_submit():

        death_date = None
        if form.status.data == "DE":
            death_date = form.death_date.data

        donor_information = {
            "age": form.age.data,
            "sex": form.sex.data,
            "status": form.status.data,
            "race": form.race.data,
            "death_date": death_date,
            "weight": form.weight.data,
            "height": form.height.data
        }

        response = requests.post(
            url_for("api.donor_new", _external=True),
            headers=get_internal_api_header(),
            json=document_information,
        )

        if response.status_code == 200:
            flash("Donor information successfully added!")
            return redirect(url_for("donor.index"))
        else:
            return abort(response.status_code)

    return render_template("donor/add.html", form=form)


@login_required
@donor.route("/edit/LIMBDON-<donor_id>", methods=["GET", "POST"])
def edit(donor_id):
    response = requests.get(
        url_for("api.donor_view", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    if response.status_code == 200:
        form = DonorCreationForm(data=response.json()["content"])

        if form.validate_on_submit():
            form_information = {
                "age": form.age.data,
                "sex": form.type.data,
                "status": form.description.data,
                "death_date": form.death_date.data,
                "weight": form.weight.data,
                "height": form.height.data,
                "race": form.race.data
            }

            edit_response = requests.put(
                url_for("api.donor_edit", id=id, _external=True),
                headers=get_internal_api_header(),
                json=form_information,
            )

            if edit_response.status_code == 200:
                flash("Donor Successfully Edited")
            else:
                flash("We have a problem: %s" % (edit_response.json()))
            return redirect(url_for("donor.view", id=id))
        return render_template(
            "donor/edit.html", donor=response.json()["content"], form=form
        )
    else:
        return response.content
