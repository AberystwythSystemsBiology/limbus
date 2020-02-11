from flask import render_template, redirect, url_for, jsonify, request, session
from .models import Sample, SampleAttributeOption, SampleAttribute, SampleAttributeTextValue, SampleAttributeTextSetting, SampleAttributeOptionValue, SampleDocumentAssociation
from ..document.models import Document, DocumentType
from .forms import SampleAttributeCreationForm, SampleCreationForm, DynamicAttributeSelectForm, p, SampleAttributionCreationFormText, PatientConsentFormSelectForm
from ..auth.models import User
from flask_login import login_required, current_user
from . import sample
from .. import db

from ..dynform import DynamicAttributeFormGenerator

from ..codegenerator import DataMatrixGenerator

from ..misc.generators import generate_random_hash

@sample.route("/")
def portal():

    info = {
        "sample_count" : db.session.query(Sample).count(),
        "sample_attr_count" : db.session.query(SampleAttribute).count(),
        "donor_count" : 0
    }


    return render_template("sample/index.html", info=info)

@sample.route("samples/")
def index():
    samples = db.session.query(Sample, User).filter(Sample.author_id == User.id).all()
    return render_template("sample/information/index.html", samples=samples)

@sample.route("view/LIMBSMP-<sample_id>", methods=["GET"])
def view(sample_id):
    sample = db.session.query(Sample).filter(Sample.id == sample_id).first()
    text_attr = db.session.query(
        SampleAttribute,
        SampleAttributeTextValue
    ).filter(
        SampleAttributeTextValue.sample_id == sample_id
    ).filter(
        SampleAttributeTextValue.sample_attribute_id == SampleAttribute.id
    ).all()

    option_attr = db.session.query(
        SampleAttribute,
        SampleAttributeOptionValue,
        SampleAttributeOption
    ).filter(
        SampleAttributeOptionValue.sample_id == sample_id
    ).filter (
        SampleAttributeOptionValue.sample_attribute_id == SampleAttribute.id
    ).filter(
        SampleAttributeOptionValue.sample_option_id == SampleAttributeOption.id
    ).all()

    ascii = DataMatrixGenerator().generate()
    print(ascii)
    associated_document = db.session.query(
        SampleDocumentAssociation, Document
    ).filter(SampleDocumentAssociation.sample_id == sample_id).filter(SampleDocumentAssociation.document_id == Document.id).all()

    return render_template("sample/information/view.html", sample=sample, text_attr=text_attr, option_attr=option_attr, associated_document=associated_document)

@sample.route("view/LIMBSMP-<sample_id>/associate_doc", methods=["GET", "POST"])
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

@sample.route("add/step_zero", methods=["GET", "POST"])
@login_required
def add_sample_pcf():
    document_selection = PatientConsentFormSelectForm()

    if document_selection.validate_on_submit():
        sample_add_hash = generate_random_hash()
        # Clear the session hash.
        session[sample_add_hash] = {}
        return redirect(url_for('sample.add_sample_attr', hash=sample_add_hash))
    return render_template("sample/information/select_document.html", form=document_selection)

@sample.route("add/step_one/<hash>", methods=["GET", "POST"])
def add_sample_attr(hash):

    # TODO: Questionnaire about Patient Consent Form and upload/selection
    #  Adjust innerjoin to accept dynamic-donor inference


    query = db.session.query(SampleAttribute).all()
    conv = {p.number_to_words(x.id) : x.id for x in query}
    attr_selection = DynamicAttributeSelectForm(query, "term")

    if attr_selection.validate_on_submit():
        attribute_ids = []

        for attr in attr_selection:
            if attr.id in conv and attr.data == True:
                attribute_ids.append(conv[attr.id])
        # TODO: </endhack>

        session[hash] = {
            "sample_attributes" : {
                "attribute_ids": attribute_ids,
                "converted_ids": conv
            }
        }
        return redirect(url_for('sample.add_sample_form', hash=hash))
    return render_template("sample/information/select_attributes.html", form=attr_selection, hash=hash)



@sample.route("add/step_two/<hash>", methods=["GET", "POST"])
def add_sample_form(hash):
    query = db.session.query(SampleAttribute).filter(SampleAttribute.id.in_(session[hash]["sample_attributes"]["attribute_ids"])).all()
    form = DynamicAttributeFormGenerator(query, SampleCreationForm).make_form()

    if form.validate_on_submit():
        sample = Sample(
            sample_type=form.sample_type.data,
            collection_date=form.collection_date.data,
            disposal_instruction=form.disposal_instruction.data,
            disposal_date = form.disposal_date.data,
            author_id=current_user.id,
            sample_status=form.sample_status.data,
            batch_number = form.batch_number.data
        )

        db.session.add(sample)
        db.session.flush()

        # TODO: Generate assoc. number using BB-TIS-DBN
        # TODO: Add attribute to form element to differ between classes.
        for attr in form:
            if attr.id not in ["csrf_token", "biobank_accession_number", "sample_status", "batch_number", "submit", "sample_type", "collection_date", "disposal_instruction"]:
                if attr.type in ["TextAreaField", "StringField"]:
                    attr_value = SampleAttributeTextValue(
                        value = attr.data,
                        sample_attribute_id = session[hash]["sample_attributes"]["converted_ids"][attr.id],
                        sample_id = sample.id,
                        author_id = current_user.id
                    )
                    db.session.add(attr_value)
                elif attr.type in ["SelectField"]:
                    option = db.session.query(SampleAttributeOption).filter(SampleAttributeOption.term == attr.data).first()

                    option_value = SampleAttributeOptionValue(
                        sample_attribute_id=session["conv"][attr.id],
                        sample_id=sample.id,
                        sample_option_id=option.id,
                        author_id = current_user.id
                    )

                    db.session.add(option_value)
        db.session.commit()

        del session[hash]

        return redirect(url_for("sample.index"))

    return render_template("sample/information/add.html", form=form, hash=hash)

# Attribute Stuff
@sample.route("attribute/")
def attribute_portal():
    sample_attributes = db.session.query(SampleAttribute, User).filter(SampleAttribute.author_id == User.id).all()
    return render_template("sample/attribute/index.html", sample_attributes=sample_attributes)

@sample.route("attribute/add/step_one", methods=["GET", "POST"])
def add_attribute():

    try:
        del session[hash]["attribute_details"]
    except KeyError:
        pass

    db.session.flush()
    form = SampleAttributeCreationForm()

    if form.validate_on_submit():
        session[hash]["attribute_details"] = {
            "term" : form.term.data,
            "type" : form.term_type.data,
            "required" : form.required.data
        }
        return redirect(url_for("sample.add_attribute_step_two"))

    return render_template("sample/attribute/add/one.html", form=form)

@sample.route("attribute/add/step_two", methods=["GET", "POST"])
def add_attribute_step_two():

    attribute_details = session["attribute_details"]

    if attribute_details["type"] == "OPTION":
        return (redirect(url_for("sample.add_attribute_step_two_option")))

    if attribute_details["type"] == "TEXT":
        form = SampleAttributionCreationFormText()
    else:
        # TODO: Need to replace with Numeric
        form = SampleAttributionCreationFormText()
    if form.validate_on_submit():

        sample_attribute = SampleAttribute(
            term = attribute_details["term"],
            type = attribute_details["type"],
            author_id = current_user.id
        )

        db.session.add(sample_attribute)
        db.session.flush()

        if attribute_details["type"] == "TEXT":
            sample_attribute_setting = SampleAttributeTextSetting(
                max_length = form.max_length.data,
                sample_attribute_id = sample_attribute.id
            )

            db.session.add(sample_attribute_setting)


        db.session.commit()

        return redirect(url_for("sample.attribute_portal"))


    return render_template("sample/attribute/add/two.html", form=form)

@sample.route("attribute/add/step_two_option", methods=["GET", "POST"])
def add_attribute_step_two_option():
    attribute_details = session["attribute_details"]
    if request.method == "POST":
        options = request.form.getlist("options[]")

        sample_attribute = SampleAttribute(
            term = attribute_details["term"],
            type = attribute_details["type"],
            author_id = current_user.id
        )

        db.session.add(sample_attribute)
        db.session.flush()


        for option in options:
            sao = SampleAttributeOption(
                term = option,
                author_id = current_user.id,
                sample_attribute_id = sample_attribute.id
            )

            db.session.add(sao)

        db.session.commit()

        # TODO: Need to get Ajax to support a return and redirect
        return url_for("sample.attribute_portal")
    else:
        return render_template("sample/attribute/add/two_option.html")

@sample.route("attribute/view/LIMBSATTR-<attribute_id>")
def view_attribute(attribute_id):
    attribute, attribute_user = db.session.query(SampleAttribute, User).filter(
        SampleAttribute.id == attribute_id
    ).filter(SampleAttribute.author_id == User.id).first()

    if attribute.type.value == "Text":
        settings = db.session.query(SampleAttributeTextSetting).filter(SampleAttributeTextSetting.sample_attribute_id == attribute.id).first()
        samples = db.session.query(SampleAttribute, Sample, User).filter(SampleAttributeTextValue.sample_attribute_id == attribute.id).filter(SampleAttributeTextValue.sample_id == Sample.id).filter(Sample.author_id == User.id).all()

    elif attribute.type.value == "Option":
        settings = db.session.query(SampleAttributeOption).filter(SampleAttributeOption.sample_attribute_id == attribute.id).all()
        samples = db.session.query(SampleAttribute, Sample, User).filter(SampleAttributeTextValue.sample_attribute_id == attribute.id).filter(SampleAttributeTextValue.sample_id == Sample.id).filter(Sample.author_id == User.id).all()

    return render_template(
        "sample/attribute/view.html",
        attribute=attribute,
        attribute_user=attribute_user,
        settings=settings,
        samples = samples
    )