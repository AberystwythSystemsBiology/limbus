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

from flask import redirect, abort, render_template, url_for, session, request, jsonify

from flask_login import current_user, login_required
from . import consent
from .. import db
from ..auth.models import User
from .forms import NewConsentFormTemplate
from ..misc.generators import generate_random_hash

from .models import *
from ..misc import clear_session

from .views import PatientConsentFormIndexView, PatientConsentFormView


@consent.route("/")
@login_required
def index():
    templates = PatientConsentFormIndexView()
    return render_template("patientconsentform/index.html", templates=templates)


@consent.route("/view/LIMBPCF-<pcf_id>")
@login_required
def view(pcf_id):
    pcf = PatientConsentFormView(pcf_id)
    return render_template("patientconsentform/view.html", pcf=pcf)


@consent.route("/add", methods=["GET", "POST"])
@login_required
def new():
    form = NewConsentFormTemplate()

    if form.validate_on_submit():
        hash = generate_random_hash()
        session["%s consent_form_info" % (hash)] = {
            "template_name": form.name.data,
            "template_version": form.version.data,
        }

        return redirect(url_for("pcf.new_two", hash=hash))

    return render_template("patientconsentform/add/one.html", form=form)


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
