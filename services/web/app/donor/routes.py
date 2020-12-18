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
from flask import (
    redirect,
    render_template,
    url_for,
    abort,
    current_app,
    session,
    flash,
    request,
)
from flask_login import login_required, current_user
import requests
from datetime import datetime

from .forms import DonorCreationForm, DonorFilterForm, DonorAssignDiagnosisForm
from ..misc import get_internal_api_header


@donor.route("/")
@login_required
def index():
    form = DonorFilterForm()
    return render_template("donor/index.html", form=form)


@donor.route("/query", methods=["POST"])
@login_required
def query_index():
    response = requests.get(
        url_for("api.donor_query", _external=True),
        headers=get_internal_api_header(),
        json=request.json,
    )

    if response.status_code == 200:
        return response.json()
    else:
        abort(response.status_code)


@donor.route("/LIMBDON-<id>")
@login_required
def view(id):
    return render_template("donor/view.html")
    
@donor.route("/LIMBDON-<id>/endpoint")
@login_required
def view_endpoint(id):
    response = requests.get(
        url_for("api.donor_view", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    if response.status_code == 200:
        return response.json()


@donor.route("/LIMBDON-<id>/diagnosis/new", methods=["GET", "POST"])
@login_required
def new_diagnosis(id):
    response = requests.get(
        url_for("api.donor_view", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    if response.status_code == 200:

        form = DonorAssignDiagnosisForm()


        if form.validate_on_submit():
            
            diagnosis_response = requests.post(
                url_for("api.donor_new_diagnosis", id=id, _external=True),
                headers=get_internal_api_header(),
                json={
                    "doid_ref": form.disease_select.data,
                    "stage": form.stage.data,
                    "diagnosis_date": str(datetime.strptime(str(form.diagnosis_date.data), "%Y-%m-%d").date()),
                    "comments": form.comments.data
                }
            )

            if diagnosis_response.status_code == 200:
                flash("Disease Annotation Added!")
                return redirect(url_for("donor.view", id=id))

            flash("Error!: %s" % diagnosis_response.json()["message"])

        return render_template("donor/diagnosis/assign.html", donor=response.json()["content"], form=form)
    else:
        return response.content

@donor.route("/disease/api/label_filter", methods=["POST"])
@login_required
def api_filter():
    query = request.json

    query_response = requests.post(
        url_for("api.doid_query_by_label", _external=True),
        headers=get_internal_api_header(),
        json=query
    )

    if query_response.status_code == 200:
        return query_response.json()
    return query_response.content

@login_required
@donor.route("/new", methods=["GET", "POST"])
def add():
    sites_response = requests.get(
        url_for("api.site_home", _external=True), headers=get_internal_api_header()
    )

    if sites_response.status_code == 200:

        form = DonorCreationForm(sites_response.json()["content"])
        if form.validate_on_submit():


            form_information = {
                "dob": str(datetime.strptime("%s-%s-1" % (form.year.data, form.month.data), "%Y-%m-%d").date()),
                "enrollment_site_id": form.site.data,
                "registration_date": str(datetime.strptime(str(form.registration_date.data), "%Y-%m-%d").date()),
                "sex": form.sex.data,
                "colour": form.colour.data,
                "status": form.status.data,
                "mpn": form.mpn.data,
                "race": form.race.data,
                "death_date": str(datetime.strptime(str(form.death_date.data), "%Y-%m-%d").date()),
                "weight": form.weight.data,
                "height": form.height.data,
            }

            response = requests.post(
                url_for("api.donor_new", _external=True),
                headers=get_internal_api_header(),
                json=form_information,
            )

            if response.status_code == 200:
                flash("Donor information successfully added!")
                return redirect(url_for("donor.index"))

            abort(response.status_code)

        return render_template("donor/add.html", form=form)
    abort(response.status_code)


@login_required
@donor.route("/edit/LIMBDON-<id>", methods=["GET", "POST"])
def edit(id):
    response = requests.get(
        url_for("api.donor_view", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    if response.status_code == 200:

        donor_info = response.json()["content"]

        donor_info["death_date"] = datetime.strptime(
            donor_info["death_date"], "%Y-%m-%d"
        )

        sites_response = requests.get(
            url_for("api.site_home", _external=True),
            headers=get_internal_api_header()
        )

        if sites_response.status_code == 200:

            form = DonorCreationForm(sites_response.json()["content"], data=donor_info)
            if form.validate_on_submit():

                death_date = None
                if form.status.data == "DE":
                    death_date = str(form.death_date.data)

                form_information = {
                    "age": form.age.data,
                    "sex": form.sex.data,
                    "status": form.status.data,
                    "death_date": death_date,
                    "weight": form.weight.data,
                    "height": form.height.data,
                    "race": form.race.data,
                }
                # Set empty field to Null
                for i in form_information:
                    form_information[i] = strconv(form_information[i])

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
