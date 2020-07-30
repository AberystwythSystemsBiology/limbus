# Copyright (C) 2019  Keiron O'Shea <keo7@aber.ac.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from flask import Blueprint, render_template, session, current_app
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


def get_internal_api_header():
    try:
        return {
            "FlaskApp": current_app.config.get("SECRET_KEY"),
            "Email": current_user.email,
        }
    except AttributeError:
        return {}


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
