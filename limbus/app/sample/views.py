from flask import render_template, redirect, url_for, jsonify, request, session
from .models import Sample, SampleAttributeOption, SampleAttribute, SampleAttributeTextValue, SampleAttributeTextSetting, SampleAttributeOptionValue, SampleDocumentAssociation
from ..document.models import Document, DocumentType
from .forms import SampleAttributeCreationForm, SampleCreationForm, DynamicAttributeSelectForm, p, SampleAttributionCreationFormText, PatientConsentFormSelectForm
from ..auth.models import User
from flask_login import login_required, current_user
from . import sample
from .. import db

from ..dynform import DynamicAttributeFormGenerator, clear_session

from ..misc.generators import generate_random_hash

from .tmp_views import *


@sample.route("view/LIMBSMP-<sample_id>/associate_doc", methods=["GET", "POST"])
@login_required
def associate_document(sample_id):
    sample = db.session.query(Sample).filter(Sample.id == sample_id).first()
    query = db.session.query(Document).all()
    conv = {p.number_to_words(x.id) : x.id for x in query}
    form = DynamicAttributeSelectForm(query, "name")
    if form.validate_on_submit():
        for attr in form:
            if attr.id in conv and attr.data == True:
                sda = SampleDocumentAssociation(
                    sample_id = sample_id,
                    document_id = conv[attr.id],
                    author_id = current_user.id
                )

                db.session.add(sda)

            db.session.commit()

            return redirect(url_for("sample.view", sample_id=sample_id))

    return render_template("sample/information/document/associate.html", sample=sample, form=form)

