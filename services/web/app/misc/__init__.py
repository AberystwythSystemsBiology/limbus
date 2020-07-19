from flask import Blueprint, render_template, session
from flask_login import current_user

misc = Blueprint("misc", __name__)

from .models import SiteInformation

from .. import db
from itertools import islice


def clear_session(hash: str) -> None:
    # Clear cookie session.
    for k, v in list(session.items()):
        if k.startswith(hash):
            del session[k]


def chunks(it, n):
    it = iter(it)
    return [x for x in iter(lambda: tuple(islice(it, n)), ())]


@misc.route("/")
def index() -> str:
    if current_user.is_authenticated:
        biobank = db.session.query(SiteInformation).first()
        return render_template("misc/panel.html", biobank=biobank)
    else:
        return render_template("misc/index.html")


@misc.route("/license")
def license() -> str:
    return render_template("misc/license.html")


@misc.route("/team")
def team() -> str:
    return render_template("misc/team.html")
