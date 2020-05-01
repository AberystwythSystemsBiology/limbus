from ..attribute import attribute

from flask_login import current_user
from flask import render_template, session, redirect, url_for, request, jsonify

from .forms import CustomAttributeCreationForm, CustomNumericAttributionCreationForm, CustomTextAttributeCreationForm

from ..misc.generators import generate_random_hash

from .models import *

from .. import db

from ..misc import clear_session

from .views import CustomAttributesIndexView, CustomAttributeView

@attribute.route("/")
def index():
    attributes = CustomAttributesIndexView()
    # TODO: Temporary fix.
    if attributes == None:
        attributes = {}
    return render_template("attribute/index.html", attributes=attributes)

@attribute.route("/view/LIMBATTR-<attr_id>")
def view(attr_id):

    cav = CustomAttributeView(attr_id)

    return "Hello World"

@attribute.route("/add", methods=["GET", "POST"])
def add():
    form = CustomAttributeCreationForm()

    if form.validate_on_submit():
        hash = generate_random_hash()
        session["%s attribute_info"] = {
            "term": form.term.data,
            "description": form.description.data,
            "element": form.element.data,
            "requried": form.required.data
        }


        if form.type.data == "TEXT":
            return redirect(url_for("attribute.add_textual", hash=hash))
        elif form.type.data == "NUMERIC":
            return redirect(url_for("attribute.add_numeric", hash=hash))
        else:
            return redirect(url_for("attribute.add_option", hash=hash))

    return render_template("attribute/add/add.html", form=form)

@attribute.route("/add/numeric/<hash>", methods=["GET", "POST"])
def add_numeric(hash):
    form = CustomNumericAttributionCreationForm()


    if form.validate_on_submit():
        attribute_info = session["%s attribute_info"]

        ca = CustomAttributes(
            term = attribute_info["term"],
            description = attribute_info["description"],
            author_id = current_user.id,
            type = CustomAttributeTypes.NUMERIC,
            element = attribute_info["element"]
        )

        db.session.add(ca)
        db.session.flush()

        measurement = form.measurement.data
        prefix = form.prefix.data

        if not form.requires_measurement.data:
            measurement = None

        if not form.requires_prefix.data:
            prefix = None

        ca_ns = CustomAttributeNumericSetting(
            custom_attribute_id = ca.id,
            measurement = measurement,
            prefix = prefix
        )

        db.session.add(ca_ns)
        db.session.commit()
        clear_session(hash)

        return redirect(url_for("attribute.index"))

    return render_template("attribute/add/numeric.html", form=form, hash=hash)

@attribute.route("/add/option/<hash>", methods=["GET", "POST"])
def add_option(hash):
    if request.method == "POST":

        options = request.form.getlist("options[]")

        attribute_info = session["%s attribute_info"]

        ca = CustomAttributes(
            term=attribute_info["term"],
            description=attribute_info["description"],
            author_id=current_user.id,
            type=CustomAttributeTypes.OPTION,
            element=attribute_info["element"]
        )

        db.session.add(ca)
        db.session.flush()

        for option in options:
            sao = CustomAttributeOption(
                term=option,
                author_id=current_user.id,
                custom_attribute_id=ca.id,
            )

            db.session.add(sao)

        db.session.commit()

        resp = jsonify({"redirect": url_for("attribute.index", _external=True)})

        clear_session(hash)
        return resp, 201, {"ContentType": "application/json"}

    return render_template("attribute/add/option.html", hash=hash)

@attribute.route("/add/textual/<hash>", methods=["GET", "POST"])
def add_textual(hash):
    form = CustomTextAttributeCreationForm()
    if form.validate_on_submit():
        attribute_info = session["%s attribute_info"]

        ca = CustomAttributes(
            term=attribute_info["term"],
            description=attribute_info["description"],
            author_id=current_user.id,
            type=CustomAttributeTypes.TEXT,
            element=attribute_info["element"]
        )

        db.session.add(ca)
        db.session.flush()

        ca_ts = CustomAttributeTextSetting(
            max_length = form.max_length.data,
            author_id = current_user.id,
            custom_attribute_id = ca.id
        )

        db.session.add(ca_ts)
        db.session.commit()

        clear_session(hash)

        return redirect(url_for("attribute.index"))


    return render_template("attribute/add/textual.html", form=form, hash=hash)