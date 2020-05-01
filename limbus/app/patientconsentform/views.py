from flask import redirect, abort, render_template, url_for, session, request, jsonify

from flask_login import current_user
from . import pcf
from .. import db
from ..auth.models import User
from .forms import NewConsentFormTemplate
from ..misc.generators import generate_random_hash
from .models import ConsentFormTemplate, ConsentFormTemplateQuestion
from ..sample.models import (
    SamplePatientConsentFormTemplateAssociation,
    Sample,
    SamplePatientConsentFormAnswersAssociation,
)


from ..misc import clear_session

from .api import *

@pcf.route("/")
def index():
    templates = (
        db.session.query(ConsentFormTemplate, User)
        .filter(ConsentFormTemplate.uploader == User.id)
        .all()
    )

    return render_template("patientconsentform/index.html", templates=templates)


@pcf.route("/view/LIMBPCF-<pcf_id>")
def view(pcf_id):
    template, uploader = (
        db.session.query(ConsentFormTemplate, User)
        .filter(ConsentFormTemplate.id == pcf_id)
        .filter(ConsentFormTemplate.uploader == User.id)
        .first_or_404()
    )

    questions = (
        db.session.query(ConsentFormTemplateQuestion)
        .filter(ConsentFormTemplateQuestion.template_id == pcf_id)
        .all()
    )
    questions = [questions[i : (i + 3)] for i in range(0, len(questions), 3)]

    assoc_samples = (
        db.session.query(SamplePatientConsentFormTemplateAssociation, Sample)
        .filter(SamplePatientConsentFormTemplateAssociation.template_id == pcf_id)
        .filter(SamplePatientConsentFormTemplateAssociation.sample_id == Sample.id)
        .all()
    )

    return render_template(
        "patientconsentform/view.html",
        template=template,
        questions=questions,
        uploader=uploader,
        assoc_samples=[x[1] for x in assoc_samples],
    )


@pcf.route("/add", methods=["GET", "POST"])
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


@pcf.route("/add/two/<hash>", methods=["GET", "POST"])
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
