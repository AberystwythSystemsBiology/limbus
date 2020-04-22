from .. import sample
from flask import render_template, session, redirect, url_for
from flask_login import login_required, current_user
from ... import db

from ...dynform import clear_session

from ...misc.generators import generate_random_hash

from ..models import *


from ..forms import (
    SampleAttributeCreationForm,
    SampleAttributionCreationFormText,
    SampleAttributeCreationFormNumeric,
)

@sample.route("attribute/")
@login_required
def attribute_portal():
    sample_attributes = []
    return render_template(
        "sample/attribute/index.html", sample_attributes=sample_attributes
    )


@sample.route("attribute/add/one", methods=["GET", "POST"])
@login_required
def add_attribute():
    form = SampleAttributeCreationForm()

    if form.validate_on_submit():
        hash = generate_random_hash()
        session["%s attribute_details" % (hash)] = {
            "term": form.term.data,
            "type": form.term_type.data,
            "required": form.required.data,
        }

        if form.term_type.data == "OPTION":
            return redirect(url_for("sample.add_attribute_step_two_option", hash=hash))
        else:
            return redirect(url_for("sample.add_attribute_step_two", hash=hash))
    return render_template("sample/attribute/add/one.html", form=form)


@sample.route("attribute/add/two/<hash>", methods=["GET", "POST"])
@login_required
def add_attribute_step_two(hash):
    attribute_details = session["%s attribute_details" % (hash)]

    if attribute_details["type"] == "TEXT":
        form = SampleAttributionCreationFormText()
    else:
        form = SampleAttributeCreationFormNumeric()

    if form.validate_on_submit():

        sample_attribute = SampleAttribute(
            term=attribute_details["term"],
            type=attribute_details["type"],
            required=attribute_details["required"],
            author_id=current_user.id,
        )

        db.session.add(sample_attribute)
        db.session.flush()

        if attribute_details["type"] == "TEXT":
            sample_attribute_setting = SampleAttributeTextSetting(
                max_length=form.max_length.data, sample_attribute_id=sample_attribute.id
            )
            db.session.add(sample_attribute_setting)
            db.session.commit()
            clear_session(hash)
            return redirect(url_for("sample.attribute_portal"))

        elif attribute_details["type"] == "NUMERIC":
            # TODO:
            pass

    return render_template("sample/attribute/add/two.html", form=form, hash=hash)


@sample.route("attribute/add/two_option/<hash>", methods=["GET", "POST"])
@login_required
def add_attribute_step_two_option(hash):

    if request.method == "POST":
        attribute_details = session["%s attribute_details" % (hash)]

        options = request.form.getlist("options[]")

        sample_attribute = SampleAttribute(
            term=attribute_details["term"],
            type=attribute_details["type"],
            author_id=current_user.id,
        )
        db.session.add(sample_attribute)
        db.session.flush()

        for option in options:
            sao = SampleAttributeOption(
                term=option,
                author_id=current_user.id,
                sample_attribute_id=sample_attribute.id,
            )

            db.session.add(sao)

        db.session.commit()

        clear_session(hash)

        resp = jsonify({"redirect": url_for("sample.attribute_portal", _external=True)})

        return resp, 201, {"ContentType": "application/json"}
    else:
        return render_template("sample/attribute/add/two_option.html", hash=hash)
