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
from flask import render_template, session, redirect, url_for, request, jsonify, abort

from .forms import (
    AttributeCreationForm,
    CustomNumericAttributionCreationForm,
    CustomTextAttributeCreationForm,
    AttributeTextSetting,
)

from .. import db
import uuid

from ..misc import get_internal_api_header

import requests

@attribute.route("/")
@login_required
def index():
    response = requests.get(
        url_for("api.attribute_home", _external=True),
        headers=get_internal_api_header()
    )

    if response.status_code == 200:
        return render_template("attribute/index.html", attributes=response.json()["content"])
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
            "element": form.element.data
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

    attribute_type = attribute_information["type"]

    if attribute_type == "TEXT":
        form = AttributeTextSetting()


    return render_template("attribute/new/additional.html", form=form, hash=hash, attribute_type=attribute_type)




'''
@attribute.route("/view/LIMBATTR-<attr_id>")
@login_required
def view(attr_id):
    cav = CustomAttributeView(attr_id)
    return render_template("attribute/view.html", attribute=cav)


@attribute.route("/add", methods=["GET", "POST"])
@login_required
def add():
    form = CustomAttributeCreationForm()

    if form.validate_on_submit():
        hash = generate_random_hash()
        session["%s attribute_info"] = {
            "term": form.term.data,
            "description": form.description.data,
            "element": form.element.data,
            "requried": form.required.data,
        }

        if form.type.data == "TEXT":
            return redirect(url_for("attribute.add_textual", hash=hash))
        elif form.type.data == "NUMERIC":
            return redirect(url_for("attribute.add_numeric", hash=hash))
        else:
            return redirect(url_for("attribute.add_option", hash=hash))

    return render_template("attribute/add/add.html", form=form)


@attribute.route("/add/numeric/<hash>", methods=["GET", "POST"])
@login_required
def add_numeric(hash):
    form = CustomNumericAttributionCreationForm()

    if form.validate_on_submit():
        attribute_info = session["%s attribute_info"]

        ca = CustomAttributes(
            term=attribute_info["term"],
            description=attribute_info["description"],
            author_id=current_user.id,
            type=CustomAttributeTypes.NUMERIC,
            element=attribute_info["element"],
        )

        db.session.add(ca)
        db.session.flush()

        measurement = form.measurement.data
        prefix = form.prefix.data

        if not form.requires_measurement.data:
            measurement = None

        if not form.requires_prefix.data:
            prefix = None

        ca_ns = CustomAttributeNumericSetting(
            custom_attribute_id=ca.id, measurement=measurement, prefix=prefix
        )

        db.session.add(ca_ns)
        db.session.commit()
        clear_session(hash)

        return redirect(url_for("attribute.index"))

    return render_template("attribute/add/numeric.html", form=form, hash=hash)


@attribute.route("/add/option/<hash>", methods=["GET", "POST"])
@login_required
def add_option(hash):
    if request.method == "POST":

        options = request.form.getlist("options[]")

        attribute_info = session["%s attribute_info"]

        ca = CustomAttributes(
            term=attribute_info["term"],
            description=attribute_info["description"],
            author_id=current_user.id,
            type=CustomAttributeTypes.OPTION,
            element=attribute_info["element"],
        )

        db.session.add(ca)
        db.session.flush()

        for option in options:
            sao = CustomAttributeOption(
                term=option, author_id=current_user.id, custom_attribute_id=ca.id
            )

            db.session.add(sao)

        db.session.commit()

        resp = jsonify({"redirect": url_for("attribute.index", _external=True)})

        clear_session(hash)
        return resp, 201, {"ContentType": "application/json"}

    return render_template("attribute/add/option.html", hash=hash)


@attribute.route("/add/textual/<hash>", methods=["GET", "POST"])
@login_required
def add_textual(hash):
    form = CustomTextAttributeCreationForm()
    if form.validate_on_submit():
        attribute_info = session["%s attribute_info"]

        ca = CustomAttributes(
            term=attribute_info["term"],
            description=attribute_info["description"],
            author_id=current_user.id,
            type=CustomAttributeTypes.TEXT,
            element=attribute_info["element"],
        )

        db.session.add(ca)
        db.session.flush()

        ca_ts = CustomAttributeTextSetting(
            max_length=form.max_length.data,
            author_id=current_user.id,
            custom_attribute_id=ca.id,
        )

        db.session.add(ca_ts)
        db.session.commit()

        clear_session(hash)

        return redirect(url_for("attribute.index"))

    return render_template("attribute/add/textual.html", form=form, hash=hash)
'''