from flask import Blueprint, render_template
from flask_login import current_user

misc = Blueprint("misc", __name__)

from ..document.models import Document, DocumentFile
from ..sample.models import Sample, SampleAttribute

from .. import db


@misc.route("/")
def index():
    if current_user.is_authenticated:
        return render_template("misc/panel.html")
    else:
        return render_template("misc/index.html")


@misc.route("/license")
def license():
    return render_template("misc/license.html")


@misc.route("/team")
def team():
    return render_template("misc/team.html")
