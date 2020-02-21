from flask import render_template, redirect, session, url_for, request
from .. import sample
from flask_login import login_required, current_user
from ... import db
from ..models import Sample, SampleAttribute, SampleAttributeOption, SampleAttributeOptionValue, SampleAttributeTextValue, SampleAttributeTextSetting
from ...dynform import clear_session
from ..forms import SampleAttributeCreationForm, SampleAttributionCreationFormText
from ...auth.models import User
from ...misc.generators import generate_random_hash


@sample.route("attribute/")
@login_required
def attribute_portal():
    sample_attributes = db.session.query(
        SampleAttribute,
        User).filter(SampleAttribute.author_id == User.id).all()
    return render_template("sample/attribute/index.html",
                           sample_attributes=sample_attributes)


@sample.route("attribute/add/one", methods=["GET", "POST"])
@login_required
def add_attribute():
    form = SampleAttributeCreationForm()
    if form.validate_on_submit():
        hash = generate_random_hash()
        session["%s attribute_details" % (hash)] = {
            "term": form.term.data,
            "type": form.term_type.data,
            "required": form.required.data
        }
        return redirect(url_for("sample.add_attribute_step_two", hash=hash))
    return render_template("sample/attribute/add/one.html", form=form)


@sample.route("attribute/add/two/<hash>", methods=["GET", "POST"])
@login_required
def add_attribute_step_two(hash):
    attribute_details = session["%s attribute_details" % (hash)]
    if attribute_details["type"] == "OPTION":
        return redirect(
            url_for("sample.add_attribute_step_two_option", hash=hash))
    if attribute_details["type"] == "TEXT":
        form = SampleAttributionCreationFormText()
    else:
        # TODO: Need to replace with Numeric
        form = SampleAttributionCreationFormText()
    if form.validate_on_submit():

        sample_attribute = SampleAttribute(term=attribute_details["term"],
                                           type=attribute_details["type"],
                                           author_id=current_user.id)

        db.session.add(sample_attribute)
        db.session.flush()

        if attribute_details["type"] == "TEXT":
            sample_attribute_setting = SampleAttributeTextSetting(
                max_length=form.max_length.data,
                sample_attribute_id=sample_attribute.id)

            db.session.add(sample_attribute_setting)

        db.session.commit()
        clear_session(hash)
        return redirect(url_for("sample.attribute_portal"))

    return render_template("sample/attribute/add/two.html", form=form)


@sample.route("attribute/add/two_option/<hash>", methods=["GET", "POST"])
@login_required
def add_attribute_step_two_option(hash):
    attribute_details = session["%s attribute_details" % (hash)]
    if request.method == "POST":
        options = request.form.getlist("options[]")

        sample_attribute = SampleAttribute(term=attribute_details["term"],
                                           type=attribute_details["type"],
                                           author_id=current_user.id)

        db.session.add(sample_attribute)
        db.session.flush()

        for option in options:
            sao = SampleAttributeOption(
                term=option,
                author_id=current_user.id,
                sample_attribute_id=sample_attribute.id)

            db.session.add(sao)

        db.session.commit()

        clear_session(hash)

        # TODO: Need to get Ajax to support a return and redirect
        return url_for("sample.attribute_portal")
    else:
        return render_template("sample/attribute/add/two_option.html",
                               hash=hash)


@sample.route("attribute/view/LIMBSATTR-<attribute_id>")
@login_required
def view_attribute(attribute_id):
    attribute, attribute_user = db.session.query(
        SampleAttribute,
        User).filter(SampleAttribute.id == attribute_id).filter(
            SampleAttribute.author_id == User.id).first()

    if attribute.type.value == "Text":
        settings = db.session.query(SampleAttributeTextSetting).filter(
            SampleAttributeTextSetting.sample_attribute_id ==
            attribute.id).first()
        samples = db.session.query(SampleAttribute, Sample, User).filter(
            SampleAttributeTextValue.sample_attribute_id == attribute.id
        ).filter(SampleAttributeTextValue.sample_id == Sample.id).filter(
            Sample.author_id == User.id).all()

    elif attribute.type.value == "Option":
        settings = db.session.query(SampleAttributeOption).filter(
            SampleAttributeOption.sample_attribute_id == attribute.id).all()
        samples = db.session.query(SampleAttribute, Sample, User).filter(
            SampleAttributeTextValue.sample_attribute_id == attribute.id
        ).filter(SampleAttributeTextValue.sample_id == Sample.id).filter(
            Sample.author_id == User.id).all()

    return render_template("sample/attribute/view.html",
                           attribute=attribute,
                           attribute_user=attribute_user,
                           settings=settings,
                           samples=samples)
