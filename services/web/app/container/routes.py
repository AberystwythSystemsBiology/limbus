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

from ..container import container
from flask import render_template, url_for, flash, redirect,abort
from flask_login import current_user, login_required
from .forms import NewContainerForm, NewFixationType, EditContainerForm,EditFixationTypeForm
import requests
from ..misc import get_internal_api_header
from ..decorators import check_if_admin

@container.route("/")
@login_required
def index():
    return render_template("container/index.html")


@container.route("/data/container")
def index_container_data():
    container_response = requests.get(
        url_for("api.container_index", _external=True),
        headers=get_internal_api_header()
    )

    return (
            container_response.text,
            container_response.status_code,
            container_response.headers.items()
    )


@container.route("/data/fixation")
def index_fixation_data():
    fixation_response = requests.get(
        url_for("api.container_fixation_index", _external=True),
        headers=get_internal_api_header()
    )

    return (
        fixation_response.text,
        fixation_response.status_code,
        fixation_response.headers.items()
    )


@container.route("/view/container/LIMBCT-<id>")
def view_container(id: int):
    response = requests.get(
        url_for("api.container_view_container", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    if response.status_code == 200:
        return render_template(
        "container/view/container.html", container=response.json()["content"]
    )

    return abort(response.status_code)
    # return render_template("container/view/container.html", id=id)


@container.route("/view/fixation/LIMBFIX-<id>")
def view_fixation_type(id: int):
    response = requests.get(
        url_for("api.container_view_fixation", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    if response.status_code == 200:
        return render_template(
            "container/view/fixation.html", fixation=response.json()["content"]
        )

    return abort(response.status_code)
    # return render_template("container/view/fixation.html", id=id)

@container.route("/view/fixation/LIMBFIX-<id>/data")
def view_fixation_data(id: int):
    fixation_response = requests.get(
        url_for("api.container_view_fixation", id=id, _external=True),
        headers=get_internal_api_header()
    )

    return (
            fixation_response.text,
            fixation_response.status_code,
            fixation_response.headers.items()
    )


@container.route("/edit/fixation/LIMBFIX-<id>/", methods=["GET", "POST"])
def edit_fixation_type(id: int):
    container_response = requests.get(
        url_for("api.container_view_fixation", id=id, _external=True),
        headers=get_internal_api_header()
    )

    container_information = container_response.json()["content"]
    if container_information["is_locked"]:
        abort(401)

    if container_response.status_code == 200:
        form = EditFixationTypeForm(
            name=container_information["container"]["name"],
            manufacturer=container_information["container"]["manufacturer"],
            description=container_information["container"]["description"],
            colour=container_information["container"]["colour"],
            used_for=container_information["container"]["used_for"],
            temperature=container_information["container"]["temperature"],
            start_hour=container_information["start_hour"],
            end_hour=container_information["end_hour"],
            formulation=container_information["formulation"]
        )

        if form.validate_on_submit():

            form_information = {
                "container": {
                    "name": form.name.data,
                    "manufacturer": form.manufacturer.data,
                    "description": form.description.data,
                    "colour": form.colour.data,
                    "used_for": form.used_for.data,
                    "temperature": form.temperature.data
                },
                "start_hour": form.start_hour.data,
                "end_hour": form.end_hour.data,
                "formulation": form.formulation.data
            }

            edit_response = requests.put(
                url_for("api.container_edit_fixation", id=id, _external=True),
                headers=get_internal_api_header(),
                json=form_information
            )

            if edit_response.status_code == 200:
                flash("Fixation Type Successfully Edited")
            else:
                flash("We have a problem: %s" % (edit_response.json()))
            return redirect(url_for("container.view_fixation_type", id=id))

        return render_template("container/edit/fixation.html", form=form, id=id)

        # return "Hello World"
    return (
        container_response.text,
        container_response.status_code,
        container_response.headers.items()
    )


@container.route("/edit/container/LIMBCT-<id>/", methods=["GET", "POST"])
def edit_container(id: int):
    container_response = requests.get(
        url_for("api.container_view_container", id=id, _external=True),
        headers=get_internal_api_header()
    )

    container_information = container_response.json()["content"]
    if container_information["is_locked"]:
        abort(401)

    container_information = container_response.json()["content"]

    if container_response.status_code == 200:
        form = EditContainerForm(
            name=container_information["container"]["name"],
            manufacturer=container_information["container"]["manufacturer"],
            description=container_information["container"]["description"],
            temperature=container_information["container"]["temperature"],
            fluid=container_information["fluid"],
            cellular=container_information["cellular"],
            tissue=container_information["tissue"],
            sample_rack=container_information["sample_rack"]
        )

        if form.validate_on_submit():

            form_information = {
                "container": {
                    "name": form.name.data,
                    "manufacturer": form.manufacturer.data,
                    "description": form.description.data,
                    "temperature": form.temperature.data
                },
                "cellular": form.cellular.data,
                "fluid": form.fluid.data,
                "tissue": form.tissue.data,
                "sample_rack": form.sample_rack.data
            }

            edit_response = requests.put(
                url_for("api.container_edit_container", id=id, _external=True),
                headers=get_internal_api_header(),
                json=form_information
            )

            if edit_response.status_code == 200:
                flash("Container Successfully Edited")
            else:
                flash("We have a problem: %s" % (edit_response.json()))
            return redirect(url_for("container.view_container", id=id))

        return render_template("container/edit/container.html", form=form, id=id)

    return (
            container_response.text,
            container_response.status_code,
            container_response.headers.items()
    )


@container.route("/view/container/LIMBCT-<id>/data")
def view_container_data(id: int):
    container_response = requests.get(
        url_for("api.container_view_container", id=id, _external=True),
        headers=get_internal_api_header()
    )

    return (
            container_response.text,
            container_response.status_code,
            container_response.headers.items()
    )


@container.route("/new/container", methods=["GET", "POST"])
@login_required
def new_container():
    form = NewContainerForm()

    if form.validate_on_submit():

        data = {
            "container": {
                "name": form.name.data,
                "manufacturer": form.manufacturer.data,
                "description": form.description.data,
                "colour": form.colour.data,
                "used_for": form.used_for.data,
                "temperature": form.temperature.data
            },
            "cellular": form.cellular.data,
            "fluid": form.fluid.data,
            "tissue": form.tissue.data,
            "sample_rack": form.sample_rack.data
        }

        new_container_response = requests.post(
            url_for("api.new_container", _external=True),
            headers=get_internal_api_header(),
            json=data
        )

        if new_container_response.status_code == 200:
            flash("Container successfully added")
            return redirect(url_for("container.index"))
        else:
            flash(new_container_response.content)
    return render_template("container/new/container.html", form=form)


@container.route("/new/fixation", methods=["GET", "POST"])
@login_required
def new_fixation_type():
    form = NewFixationType()

    if form.validate_on_submit():

        data = {
            "container": {
                "name": form.name.data,
                "manufacturer": form.manufacturer.data,
                "description": form.description.data,
                "colour": form.colour.data,
                "used_for": form.used_for.data,
                "temperature": form.temperature.data
            },
            "start_hour": form.start_hour.data,
            "end_hour": form.end_hour.data,
            "formulation": form.formulation.data
        }

        new_container_response = requests.post(
            url_for("api.new_fixation_type", _external=True),
            headers=get_internal_api_header(),
            json=data
        )

        if new_container_response.status_code == 200:
            flash("Fixation Type successfully added")
            return redirect(url_for("container.index"))
        else:
            flash(new_container_response.content)

    return render_template("container/new/fixation.html", form=form)

@container.route("/lock/container/LIMBCT-<id>")
@login_required
@check_if_admin
def lock_container(id:int):
    container_response = requests.get(
        url_for("api.container_view_container", id=id, _external=True),
        headers=get_internal_api_header()
    )
    if container_response.status_code == 200:
        lock_container_response = requests.get(
            url_for("api.container_lock_container", id=id, _external=True),
            headers=get_internal_api_header()
        )
        if lock_container_response.status_code == 200:
            if lock_container_response.json()["content"]:
                flash("Successfully Locked")
            else:
                flash("Successfully Unlocked")
        else:
            flash(lock_container_response.status_code)
        return redirect(url_for("container.view_container", id=id))
    abort(container_response.status_code)

@container.route("/lock/fixation/LIMBFIX-<id>")
@login_required
@check_if_admin
def lock_fixation(id:int):
    fixation_response = requests.get(
        url_for("api.container_view_fixation", id=id, _external=True),
        headers=get_internal_api_header()
    )
    if fixation_response.status_code == 200:
        lock_fixation_response = requests.get(
            url_for("api.container_lock_fixation", id=id, _external=True),
            headers=get_internal_api_header()
        )
        if lock_fixation_response.status_code == 200:
            if lock_fixation_response.json()["content"]:
                flash("Successfully Locked")
            else:
                flash("Successfully Unlocked")
        else:
            flash(lock_fixation_response.status_code)
        return redirect(url_for("container.view_fixation_type", id=id))
    abort(fixation_response.status_code)