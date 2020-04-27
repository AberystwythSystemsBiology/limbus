from ..attribute import attribute

from flask import render_template

from .forms import CustomAttributeCreationForm, CustomNumericAttributionCreationForm

@attribute.route("/")
def index():
    return render_template("attribute/index.html")

@attribute.route("/add")
def add_one():
    form = CustomAttributeCreationForm()

    if form.validate_on_submit():
        pass

    return render_template("attribute/add/one.html", form=form)

@attribute.route("/add/numeric/<hash>")
def add_numeric(hash):
    form = CustomNumericAttributionCreationForm()
    return render_template("attribute/add/numeric.html", form=form)

@attribute.route("/add/option/<hash>")
def add_option(hash):
    pass

@attribute.route("/add/textual/<hash>")
def add_textual(hash):
    pass