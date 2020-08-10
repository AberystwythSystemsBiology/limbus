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

from ..attribute import attribute

from flask_login import current_user, login_required
from flask import (
    render_template,
    session,
    redirect,
    url_for,
    request,
    jsonify,
    abort,
    flash,
)

from .forms import (
    AttributeCreationForm,
    CustomNumericAttributionCreationForm,
    CustomTextAttributeCreationForm,
    AttributeTextSetting,
    AttributeOptionCreationForm,
)

from .. import db
import uuid

from ..misc import get_internal_api_header

import requests


@attribute.route("/")
@login_required
def index():
    response = requests.get(
        url_for("api.attribute_home", _external=True), headers=get_internal_api_header()
    )

    if response.status_code == 200:
        return render_template(
            "attribute/index.html", attributes=response.json()["content"]
        )
    else:
        return response.content


@attribute.route("/new", methods=["GET", "POST"])
@login_required
def new():
    form = AttributeCreationForm()

    if form.validate_on_submit():
        hash = uuid.uuid4().hex

        session["%s attribute_information" % (hash)] = {
            "term": form.term.data,
            "accession": form.term.data,
            "ref": form.ref.data,
            "description": form.description.data,
            "type": form.type.data,
            "element_type": form.element_type.data,
        }

        return redirect(url_for("attribute.new_step_two", hash=hash))

    return render_template("attribute/new.html", form=form)


@attribute.route("/new/additional_information/<hash>", methods=["GET", "POST"])
@login_required
def new_step_two(hash):
    try:
        attribute_information = session["%s attribute_information" % (hash)]
    except KeyError:
        return abort(500)

    submit = False

    attribute_type = attribute_information["type"]
    if attribute_type == "OPTION":
        form = None
        additional_information = {}
        submit = True
    if attribute_type == "TEXT":
        form = AttributeTextSetting()
        if form.validate_on_submit():
            additional_information = {
                "max_length": form.max_length.data,
                "type": form.type.data,
            }
            submit = True

    elif attribute_type == "NUMERIC":
        form = CustomNumericAttributionCreationForm()
        if form.validate_on_submit():
            additional_information = {
                "measurement": form.measurement.data,
                "symbol": form.symbol.data,
            }
            submit = True

    if submit:
        response = requests.post(
            url_for("api.attribute_new_attribute", _external=True),
            headers=get_internal_api_header(),
            json={
                "attribute_information": attribute_information,
                "additional_information": additional_information,
            },
        )

        if response.status_code == 200:
            flash("Submitted")
            return redirect(url_for("attribute.index"))
        else:
            flash("Something has happened :( %s" % response.json())

    return render_template(
        "attribute/new/additional.html",
        form=form,
        hash=hash,
        attribute_type=attribute_type,
    )


@attribute.route("/LIMBATTR-<id>/option/new", methods=["GET", "POST"])
@login_required
def new_option(id):
    response = requests.get(
        url_for("api.attribute_view_attribute", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    if response.status_code != 200:
        return response.content

    form = AttributeOptionCreationForm()

    if form.validate_on_submit():
        option_values = {
            "ref": form.ref.data,
            "accession": form.accession.data,
            "term": form.term.data,
        }

        submit_response = requests.post(
            url_for("api.attribute_new_option", id=id, _external=True),
            headers=get_internal_api_header(),
            json=option_values,
        )

        if submit_response.status_code == 200:
            flash("Option added")
            return redirect(url_for("attribute.view", id=id))
        else:
            flash("Something has happened :( %s" % response.json())
    return render_template("attribute/new/option.html", form=form, attribute_id=id)


@attribute.route("/LIMBATTR-<id>")
@login_required
def view(id):
    response = requests.get(
        url_for("api.attribute_view_attribute", id=id, _external=True),
        headers=get_internal_api_header(),
    )
    if response.status_code == 200:
        return render_template(
            "attribute/view.html", attribute=response.json()["content"]
        )
    else:
        return response.content
