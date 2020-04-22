from .. import sample
from flask import render_template, wrappers
from flask_login import login_required

from ..views import SamplesIndexView

from .attributes import *
from .sample import *
from .add import *
from .aliquot import *

@sample.route("/")
@login_required
def sap_portal() -> str:
    return render_template("sample/index.html")

@sample.route("samples/")
@login_required
def index() -> str:
    samples = SamplesIndexView().get_attributes()
    return render_template("sample/information/index.html", samples=samples)
