from ..database import db
from .models import SiteInformation

from . import misc
from flask import render_template, session, current_app
from flask_login import current_user

@misc.route("/")
def index() -> str:
    if current_user.is_authenticated:
        biobank = SiteInformation.query.first()
        return render_template("misc/panel.html", biobank=biobank)
    else:
        return render_template("misc/index.html")


@misc.route("/license")
def license() -> str:
    return render_template("misc/license.html")


@misc.route("/team")
def team() -> str:
    return render_template("misc/team.html")
