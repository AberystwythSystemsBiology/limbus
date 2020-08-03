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
    return render_template("consent/index.html", templates={})


@consent.route("/view/LIMBPCF-<pcf_id>")
@login_required
def view(pcf_id):
    pcf = PatientConsentFormView(pcf_id)
    return render_template("patientconsentform/view.html", pcf=pcf)


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


@consent.route("/add/two/<hash>", methods=["GET", "POST"])
@login_required
def new_two(hash):
    if request.method == "POST":
        questions = request.form.getlist("questions[]")

        consent_form_info = session["%s consent_form_info" % (hash)]

        cfi = ConsentFormTemplate(
            name=consent_form_info["template_name"],
            uploader=current_user.id,
            version=consent_form_info["template_version"],
        )

        db.session.add(cfi)
        db.session.flush()

        cfi_id = cfi.id

        for q in questions:
            cf_question = ConsentFormTemplateQuestion(
                question=q, uploader=current_user.id, template_id=cfi_id
            )

            db.session.add(cf_question)

        db.session.commit()

        resp = jsonify({"redirect": url_for("pcf.view", pcf_id=cfi_id, _external=True)})

        clear_session(hash)
        return resp, 200, {"ContentType": "application/json"}
    return render_template("patientconsentform/add/two.html")
