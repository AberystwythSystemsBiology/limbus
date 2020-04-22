from flask import render_template, redirect, session, url_for, request, jsonify
from .. import sample
from flask_login import login_required, current_user
from ... import db
from ..models import (
    Sample,
    SampleAttribute,
    SampleAttributeOption,
    SampleAttributeOptionValue,
    SampleAttributeTextValue,
    SampleAttributeTextSetting,
)
from ...dynform import clear_session

from ...auth.models import User
from ...misc.generators import generate_random_hash


@sample.route("attribute/")
@login_required
def attribute_portal():
    sample_attributes = (
        db.session.query(SampleAttribute, User)
        .filter(SampleAttribute.author_id == User.id)
        .all()
    )
    return render_template(
        "sample/attribute/index.html", sample_attributes=sample_attributes
    )




@sample.route("attribute/view/LIMBSATTR-<attribute_id>")
@login_required
def view_attribute(attribute_id):
    attribute, attribute_user = (
        db.session.query(SampleAttribute, User)
        .filter(SampleAttribute.id == attribute_id)
        .filter(SampleAttribute.author_id == User.id)
        .first()
    )

    if attribute.type.value == "Text":
        settings = (
            db.session.query(SampleAttributeTextSetting)
            .filter(SampleAttributeTextSetting.sample_attribute_id == attribute.id)
            .first()
        )
        samples = (
            db.session.query(SampleAttribute, Sample, User)
            .filter(SampleAttributeTextValue.sample_attribute_id == attribute.id)
            .filter(SampleAttributeTextValue.sample_id == Sample.id)
            .filter(Sample.author_id == User.id)
            .all()
        )

    elif attribute.type.value == "Option":
        settings = (
            db.session.query(SampleAttributeOption)
            .filter(SampleAttributeOption.sample_attribute_id == attribute.id)
            .all()
        )
        samples = (
            db.session.query(SampleAttribute, Sample, User)
            .filter(SampleAttributeTextValue.sample_attribute_id == attribute.id)
            .filter(SampleAttributeTextValue.sample_id == Sample.id)
            .filter(Sample.author_id == User.id)
            .all()
        )

    return render_template(
        "sample/attribute/view.html",
        attribute=attribute,
        attribute_user=attribute_user,
        settings=settings,
        samples=samples,
    )
