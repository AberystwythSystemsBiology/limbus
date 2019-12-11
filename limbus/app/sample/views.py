from flask import render_template, redirect, url_for

from .models import Sample, Donor, SampleAttribute

from .forms import SampleAttributeCreationForm

from ..auth.models import User

from flask_login import login_required, current_user

from . import sample

from .. import db

@sample.route("/")
def index():
    return render_template("sample/index.html")

@sample.route("sample/add")
def add_sample():
    return "Hello World"

@sample.route("attribute/")
def attribute_portal():
    sample_attributes = db.session.query(SampleAttribute).all()

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