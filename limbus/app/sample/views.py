from flask import render_template, redirect, url_for, jsonify

from .models import Sample, Donor, SampleAttribute

from .forms import SampleAttributeCreationForm, SampleCreationForm

from ..auth.models import User

from flask_login import login_required, current_user

from . import sample

from .. import db

import app

@sample.route("/")
def index():
    return render_template("sample/index.html")

@sample.route("api/attributes")
def get_sample_attributes():
    attributes = {}

    for attribute in db.session.query(SampleAttribute).all():
        attributes[attribute.id] = {
            "TERM": attribute.term,
            "ACCESSION": attribute.accession,
            "REF": attribute.ref,
            "TYPE": attribute.type.value,
            "CREATION DATE": attribute.creation_date,
            "REQUIRED": attribute.required
        }

    return jsonify(attributes)


@sample.route("sample/add", methods=["GET", "POST"])
def add_sample():
    form = SampleCreationForm()
    if form.validate_on_submit():
        sample = Sample(
            sample_type = form.sample_type,
            collection_date = form.collection_date,
            disposal_instruction = form.disposal_instruction
        )

        db.session.add(sample)
        db.session.commit()

        return redirect(url_for("sample.index"))
    return render_template("sample/add.html", form=form)

@sample.route("sample/view")
def view_samples():
    return render_template("sample/view.html")

# Attribute Stuff

@sample.route("attribute/")
def attribute_portal():
    sample_attributes = db.session.query(SampleAttribute, User).filter(SampleAttribute.author_id == User.id).all()
    return render_template("sample/attribute/index.html", sample_attributes=sample_attributes)

@sample.route("attribute/add", methods=["GET", "POST"])
def add_attribute():
    form = SampleAttributeCreationForm()
    if form.validate_on_submit():
        sample_attribute = SampleAttribute(
            term = form.term.data,
            type = form.term_type.data,
            author_id = current_user.id
        )

        db.session.add(sample_attribute)
        db.session.commit()

        return redirect(url_for("sample.index"))
    return render_template("sample/attribute/add.html", form=form)

@sample.route("attribute/view/<attribute_id>")
def view_attribute(attribute_id):
    attribute, attribute_user = db.session.query(SampleAttribute, User).filter(
        SampleAttribute.id == attribute_id
    ).filter(SampleAttribute.author_id == User.id).first()
    return render_template("sample/attribute/view.html", attribute=attribute, attribute_user=attribute_user)