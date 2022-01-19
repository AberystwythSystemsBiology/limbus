# Copyright (C) 2022  Keiron O'Shea <keo7@aber.ac.uk>
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


from flask import Blueprint
import inspect

misc = Blueprint("misc", __name__)


from flask import session, current_app
from flask_login import current_user


from flask import current_app


def clear_session(hash: str) -> None:
    # Clear cookie session.
    for k, v in list(session.items()):
        if k.startswith(hash):
            del session[k]


def get_internal_api_header(tokenuser=None):

    print("\tCalled from: ", inspect.stack()[1][3])

    if tokenuser == None:
        email = current_user.email
    else:
        email = tokenuser.email

    return {"FlaskApp": current_app.config.get("SECRET_KEY"), "Email": email}


from .routes import *
from .types import flask_return_union
