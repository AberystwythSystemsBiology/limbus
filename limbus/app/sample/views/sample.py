from flask import render_template, redirect, session, url_for
from flask_login import current_user

from .. import sample
from flask_login import login_required
from ... import db

from ..models import *

from ...document.models import Document, PatientConsentForm

from ...auth.models import User

from ...processing.models import ProcessingTemplate

from ..forms import (
    SampleCreationForm,
    DynamicAttributeSelectForm,
    p,
    PatientConsentFormSelectForm,
    PatientConsentQuestionnaire,
    SampleTypeSelectForm,
    ProtocolTemplateSelectForm,
)

from ...dynform import DynamicAttributeFormGenerator, clear_session

from ...misc.generators import generate_random_hash

from ...patientconsentform.models import (
    ConsentFormTemplate,
    ConsentFormTemplateQuestion,
)


@sample.route("view/LIMBSMP-<sample_id>")
@login_required
def view(sample_id):
    sample = db.session.query(Sample).filter(Sample.id == sample_id).first()
    text_attr = (
        db.session.query(SampleAttribute, SampleAttributeTextValue)
        .filter(SampleAttributeTextValue.sample_id == sample_id)
        .filter(SampleAttributeTextValue.sample_attribute_id == SampleAttribute.id)
        .all()
    )

    option_attr = (
        db.session.query(
            SampleAttribute, SampleAttributeOptionValue, SampleAttributeOption
        )
        .filter(SampleAttributeOptionValue.sample_id == sample_id)
        .filter(SampleAttributeOptionValue.sample_attribute_id == SampleAttribute.id)
        .filter(SampleAttributeOptionValue.sample_option_id == SampleAttributeOption.id)
        .all()
    )

    associated_document = (
        db.session.query(SampleDocumentAssociation, Document)
        .filter(SampleDocumentAssociation.sample_id == sample_id)
        .filter(SampleDocumentAssociation.document_id == Document.id)
        .all()
    )

    _, consent_template = (
        db.session.query(
            SamplePatientConsentFormTemplateAssociation, ConsentFormTemplate
        )
        .filter(SamplePatientConsentFormTemplateAssociation.sample_id == sample_id)
        .filter(
            SamplePatientConsentFormTemplateAssociation.template_id
            == ConsentFormTemplate.id
        )
        .first_or_404()
    )

    _, template = (
        db.session.query(SampleProcessingTemplateAssociation, ProcessingTemplate)
        .filter(SampleProcessingTemplateAssociation.sample_id == sample_id)
        .filter(
            ProcessingTemplate.id == SampleProcessingTemplateAssociation.template_id
        )
        .first_or_404()
    )

    return render_template(
        "sample/sample/view.html",
        sample=sample,
        text_attr=text_attr,
        option_attr=option_attr,
        associated_document=associated_document,
        consent_template=consent_template,
        protocol=template,
    )


@sample.route("view/LIMBSMP-<sample_id>/pcf")
def pcf_view(sample_id):

    association, template = (
        db.session.query(
            SamplePatientConsentFormTemplateAssociation, ConsentFormTemplate
        )
        .filter(SamplePatientConsentFormTemplateAssociation.sample_id == sample_id)
        .filter(
            ConsentFormTemplate.id
            == SamplePatientConsentFormTemplateAssociation.template_id
        )
        .first_or_404()
    )

    """
        Need to return all possible questions, and then answers.
    """

    answers = (
        db.session.query(SamplePatientConsentFormAnswersAssociation,)
        .filter(
            SamplePatientConsentFormAnswersAssociation.sample_pcf_association_id
            == association.id
        )
        .all()
    )

    answers_id = [x.checked for x in answers]

    questions = (
        db.session.query(ConsentFormTemplateQuestion)
        .filter(ConsentFormTemplateQuestion.template_id == template.id)
        .all()
    )


    class PCFView:
        def __init__(self):
            self.sample_info = {"id": sample_id}

            self.template_info = {
                "id": template.id,
                "name": template.name,
                "association_time": association.creation_date,
            }

            self.questionnaire = [
                {"question": x.question, "answer": x.id in answers_id}
                for x in questions
            ]

    return render_template("sample/sample/pcf/view.html", pcf_view=PCFView())


"""
    Add New Sample: The following code relates to the addition of new samples. 
"""


@sample.route("add/one", methods=["GET", "POST"])
@login_required
def add_sample_pcf():
    document_selection, pcf_documents = PatientConsentFormSelectForm()

    template_count = db.session.query(ProcessingTemplate).count()

    if document_selection.validate_on_submit():
        sample_add_hash = generate_random_hash()
        session[
            "%s consent_id" % (sample_add_hash)
        ] = document_selection.form_select.data

        return redirect(url_for("sample.add_sample_pcf_data", hash=sample_add_hash))
    return render_template(
        "sample/sample/add/step_one.html",
        form=document_selection,
        template_count=template_count,
        pcf_documents=pcf_documents,
    )


@sample.route("add/two/<hash>", methods=["GET", "POST"])
@login_required
def add_sample_pcf_data(hash):
    t_id = session["%s consent_id" % (hash)]
    pcf = (
        db.session.query(ConsentFormTemplate)
        .filter(ConsentFormTemplate.id == t_id)
        .first_or_404()
    )
    pcf_questions = (
        db.session.query(ConsentFormTemplateQuestion)
        .filter(ConsentFormTemplateQuestion.template_id == t_id)
        .all()
    )
    questionnaire = PatientConsentQuestionnaire(pcf_questions)
    conv = {p.number_to_words(x.id): x.id for x in pcf_questions}

    if questionnaire.validate_on_submit():
        ticked = []
        for q in questionnaire:
            if q.type == "BooleanField":
                if q.data:
                    ticked.append(conv[q.name])

        session["%s checked_consent" % (hash)] = ticked
        return redirect(url_for("sample.select_sample_type", hash=hash))

    return render_template(
        "sample/sample/add/step_two.html",
        hash=hash,
        pcf=pcf,
        questionnaire=questionnaire,
    )


@sample.route("add/three/<hash>", methods=["GET", "POST"])
@login_required
def select_sample_type(hash):
    form = SampleTypeSelectForm()

    if form.validate_on_submit():
        session["%s sample_type" % (hash)] = form.sample_type.data

        return redirect(url_for("sample.select_processing_protocol", hash=hash))

    return render_template("sample/sample/add/step_three.html", form=form, hash=hash)


@sample.route("add/four/<hash>", methods=["GET", "POST"])
def select_processing_protocol(hash):
    templates = (
        db.session.query(ProcessingTemplate)
        .filter(ProcessingTemplate.sample_type == session["%s sample_type" % (hash)])
        .all()
    )
    form, _ = ProtocolTemplateSelectForm(templates)

    if form.validate_on_submit():
        session["%s processing_protocol" % (hash)] = {
            "protocol_id": form.form_select.data,
            "processing_date": form.processing_date.data,
            "processing_time": form.processing_time.data.strftime("%H:%M:%S")
        }
        return redirect(url_for("sample.add_sample_attr", hash=hash))

    return render_template(
        "sample/sample/add/step_four.html",
        templates=len(templates),
        form=form,
        hash=hash,
    )


@sample.route("add/five/<hash>", methods=["GET", "POST"])
@login_required
def add_sample_attr(hash):

    query = db.session.query(SampleAttribute).all()
    conv = {p.number_to_words(x.id): x.id for x in query}
    attr_selection = DynamicAttributeSelectForm(query, "term")

    if attr_selection.validate_on_submit():
        attribute_ids = []
        for attr in attr_selection:
            if attr.id in conv and attr.data == True:
                attribute_ids.append(conv[attr.id])

        session["%s sample_attributes" % (hash)] = attribute_ids
        session["%s converted_ids" % (hash)] = conv

        return redirect(url_for("sample.add_sample_form", hash=hash ))
    return render_template(
        "sample/sample/add/step_five.html", form=attr_selection, hash=hash, num_attr=len(query)
    )


@sample.route("add/six/<hash>", methods=["GET", "POST"])
@login_required
def add_sample_form(hash):
    query = (
        db.session.query(SampleAttribute)
        .filter(SampleAttribute.id.in_(session["%s sample_attributes" % (hash)]))
        .all()
    )
    form = DynamicAttributeFormGenerator(query, SampleCreationForm).make_form()

    if form.validate_on_submit():
        sample = Sample(
            sample_type=session["%s sample_type" % (hash)],
            collection_date=form.collection_date.data,
            disposal_instruction=form.disposal_instruction.data,
            disposal_date=form.disposal_date.data,
            author_id=current_user.id,
            sample_status=form.sample_status.data,
        )

        db.session.add(sample)
        db.session.flush()

        # TODO: Add attribute to form element to differ between classes.

        for attr in form:
            if attr.id not in [
                "csrf_token",
                "biobank_accession_number",
                "sample_status",
                "batch_number",
                "submit",
                "sample_type",
                "collection_date",
                "disposal_instruction",
            ]:
                if attr.type in ["TextAreaField", "StringField"]:
                    attr_value = SampleAttributeTextValue(
                        value=attr.data,
                        sample_attribute_id=session["%s converted_ids" % (hash)][
                            attr.id
                        ],
                        sample_id=sample.id,
                        author_id=current_user.id,
                    )
                    db.session.add(attr_value)

                elif attr.type in ["SelectField"]:
                    option = (
                        db.session.query(SampleAttributeOption)
                        .filter(SampleAttributeOption.term == attr.data)
                        .first()
                    )

                    option_value = SampleAttributeOptionValue(
                        sample_attribute_id=session["%s converted_ids" % (hash)][
                            attr.id
                        ],
                        sample_id=sample.id,
                        sample_option_id=option.id,
                        author_id=current_user.id,
                    )

                    db.session.add(option_value)

        spcfta = SamplePatientConsentFormTemplateAssociation(
            sample_id=sample.id,
            template_id=session["%s consent_id" % (hash)],
            author_id=current_user.id,
        )

        db.session.add(spcfta)
        db.session.flush()

        spta = SampleProcessingTemplateAssociation(
            sample_id=sample.id,
            template_id=session["%s processing_protocol" % (hash)],
            author_id=current_user.id,
        )

        db.session.add(spta)
        db.session.flush()

        for answer in session["%s checked_consent" % (hash)]:
            spcfaa = SamplePatientConsentFormAnswersAssociation(
                sample_pcf_association_id=spcfta.id,
                checked=answer,
                author_id=current_user.id,
            )

            db.session.add(spcfaa)

        db.session.commit()

        clear_session(hash)

        return redirect(url_for("sample.index"))

    return render_template("sample/sample/add/step_six.html", form=form, hash=hash)


@sample.route("view/LIMBSMP-<sample_id>/associate_doc", methods=["GET", "POST"])
@login_required
def associate_document(sample_id):
    sample = db.session.query(Sample).filter(Sample.id == sample_id).first()
    query = db.session.query(Document).all()
    conv = {p.number_to_words(x.id): x.id for x in query}
    form = DynamicAttributeSelectForm(query, "name")

    if form.validate_on_submit():
        for attr in form:
            if attr.id in conv and attr.data == True:
                sda = SampleDocumentAssociation(
                    sample_id=sample_id,
                    document_id=conv[attr.id],
                    author_id=current_user.id,
                )

                db.session.add(sda)

            db.session.commit()

            return redirect(url_for("sample.view", sample_id=sample_id))

    return render_template(
        "sample/information/document/associate.html", sample=sample, form=form
    )
