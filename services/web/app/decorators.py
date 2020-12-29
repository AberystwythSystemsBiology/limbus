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

from flask import abort, current_app, request
from flask_login import login_user, logout_user, current_user
from functools import wraps
import inspect

from .database import UserAccount, UserAccountToken


def check_if_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_admin:
            return f(*args, **kwargs)
        return abort(401)

    return decorated_function


def requires_access_level(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        pass

    return decorated_view()


def token_required(f):
    """

    :param f:
    :return:
    """

    def internal_request():
        email = request.headers["Email"].replace('"', "")
        secret = request.headers["FlaskApp"].replace('"', "")
        user = UserAccount.query.filter_by(email=email).first()
        if current_app.config.get("SECRET_KEY") == secret and user != None:
            return True, user
        return False, None

    def external_request():
        email = request.headers["Email"].replace('"', "")
        token = request.headers["Token"].replace('"', "")

        user = UserAccount.query.filter_by(email=email).first()

        if user != None:
            user_token = UserAccountToken.query.filter_by(user_id=user.id).first()
            if user_token != None:
                if user_token.verify_token(token):
                    return True, user
        return False, None

    @wraps(f)
    def decorated_function(*args, **kwargs):

        # Default check values.
        check, user = False, None
        # Internal Requests
        if "Flaskapp" in request.headers:
            check, user = internal_request()
            if check:
                if "tokenuser" in inspect.getfullargspec(f).args:
                    kwargs["tokenuser"] = user
                return f(*args, **kwargs)
            return abort(401)
        # External Requests
        elif "Token" in request.headers:
            check, user = external_request()
            if check:
                if "tokenuser" in inspect.getfullargspec(f).args:
                    kwargs["tokenuser"] = user
                return f(*args, **kwargs)
            else:
                return {"success": False, "message": "You are not authorised to view this page."}, 401

    return decorated_function


def as_kryten(f):
    """
    If you decorate a view with this, it will log you in to the bot account and allow you to enter biobank data.
    If Kryten is not present, it returns a 401.

    For example::

        @app.route("/setup")
        @as_kryten
        def setup_index():
            return "I am %s" % current_user.first_name

    Would return the view as Kryten.

    :param f: The view function to decorate.
    :return: function
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        kryten = UserAccount.query.filter_by(
            email="kryten@jupiterminingcorp.co.uk"
        ).first()
        if kryten is None:
            return abort(401)
        login_user(kryten)
        return f(*args, **kwargs)

    return decorated_function


def setup_mode(f):
    """

    This decorator should only be used within the setup context.

    If you decorate a view with this, it will check to see if a user account is present in the database before calling
    the actual view. If no user is present, it calls a 401. For example::

        @app.route("/setup")
        @check_if_user
        def setup_index():
            pass

    :param f: The view function to decorate
    :return: function
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if (
            current_user.email != "kryten@jupiterminingcorp.co.uk"
            or len(UserAccount.query.all()) > 1
        ):
            return abort(401)
        return f(*args, **kwargs)

    return decorated_function
