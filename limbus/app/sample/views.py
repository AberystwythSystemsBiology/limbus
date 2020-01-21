from flask import render_template, redirect, url_for, jsonify, request, session
from .models import Sample, SampleAttributeOption, SampleAttribute, SampleAttributeTextValue, SampleAttributeTextSetting, SampleAttributeOptionValue
from .forms import SampleAttributeCreationForm, SampleCreationForm, DynamicAttributeSelectForm, p, SampleAttributionCreationFormText
from ..auth.models import User
from flask_login import login_required, current_user
from . import sample
from .. import db

from ..dynform import DynamicAttributeFormGenerator


@sample.route("/")
def portal():
    return render_template("sample/index.html")

@sample.route("samples/")
def index():
    samples = db.session.query(Sample, User).filter(Sample.author_id == User.id).all()
    return render_template("sample/information/index.html", samples=samples)

@sample.route("view/<sample_id>", methods=["GET"])
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


    return render_template("sample/information/view.html", sample=sample, text_attr=text_attr, option_attr=option_attr)

@sample.route("add/", methods=["GET", "POST"])
def add_sample():
    session["attribute_ids"] = []

    query = db.session.query(SampleAttribute).all()
    conv = {p.number_to_words(x.id) : x.id for x in query}
    attr_selection = DynamicAttributeSelectForm(query)

    if attr_selection.validate_on_submit():
        # TODO: <hack>
        attribute_ids = []
        for attr in attr_selection:
            if attr.id in conv and attr.data == True:
                attribute_ids.append(conv[attr.id])
        # TODO: </endhack>

        session["attribute_ids"] = attribute_ids
        session["conv"] = conv

        return redirect(url_for('sample.add_sample_stwo'))
    return render_template("sample/information/select_attributes.html", form=attr_selection)

@sample.route("add/sample_info", methods=["GET", "POST"])
def add_sample_stwo():
    query = db.session.query(SampleAttribute).filter(SampleAttribute.id.in_(session["attribute_ids"])).all()

    form = DynamicAttributeFormGenerator(query, SampleCreationForm).make_form()

    if form.validate_on_submit():
        sample = Sample(
            sample_type=form.sample_type.data,
            collection_date=form.collection_date.data,
            disposal_instruction=form.disposal_instruction.data,
            disposal_date = form.disposal_date.data,
            author_id=current_user.id
        )

        db.session.add(sample)
        db.session.flush()

        for attr in form:
            if attr.id not in ["csrf_token", "submit", "sample_type", "collection_date", "disposal_instruction"]:
                if attr.type in ["TextAreaField", "StringField"]:
                    attr_value = SampleAttributeTextValue(
                        value = attr.data,
                        sample_attribute_id = session["conv"][attr.id],
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

        return redirect(url_for("sample.index"))

    return render_template("sample/information/add.html", form=form)

# Attribute Stuff
@sample.route("attribute/")
def attribute_portal():
    sample_attributes = db.session.query(SampleAttribute, User).filter(SampleAttribute.author_id == User.id).all()
    return render_template("sample/attribute/index.html", sample_attributes=sample_attributes)

@sample.route("attribute/add/step_one", methods=["GET", "POST"])
def add_attribute():

    session["attribute_details"] = None

    db.session.flush()
    form = SampleAttributeCreationForm()

    if form.validate_on_submit():
        session["attribute_details"] = {
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