from flask import render_template

from .models import Sample, Donor

from ..auth.models import User

from . import sample

from .. import db

@sample.route("/")
def index():
    return render_template("sample/index.html")