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

from binascii import hexlify
from functools import wraps
from logging import error
from os import urandom

from flask import render_template
from werkzeug.exceptions import *
import os
from random import choice


error_handlers = []

sad = [
    "😐",
    "😑",
    "😒",
    "😓",
    "😔",
    "😕",
    "😖",
    "😝",
    "😞",
    "😟",
    "😠",
    "😡",
    "😢",
    "😣",
    "😥",
    "😦",
    "😧",
    "😨",
    "😩",
    "😪",
    "😫",
    "😭",
    "😮",
    "😯",
    "😰",
    "😱",
    "😲",
    "😵",
    "😶",
    "😾",
    "😿",
    "🙀",
]


def errorhandler(code_or_exception):
    def decorator(func):
        error_handlers.append({"func": func, "code_or_exception": code_or_exception})

        @wraps(func)
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapped

    return decorator


def handle_error(e, code, json=False):
    if json:
        return {"message": e}, code
    return (
        render_template(
            "error.html", e=code, smiley=choice(sad), text=e, title="{}".format(code)
        ),
        code,
    )


@errorhandler(Unauthorized.code)
def unauthorised(e="401: Unauthorised", json=False):
    return handle_error(e, Unauthorized.code, json)


@errorhandler(NotFound.code)
def not_found(e="404: Not Found", json=False):
    return handle_error(
        e if "check your spelling" not in "{}".format(e) else "404: Not Found",
        NotFound.code,
        json,
    )


@errorhandler(Forbidden.code)
def forbidden(e="403: Forbidden", json=False):
    return handle_error(e, Forbidden.code, json)


@errorhandler(MethodNotAllowed.code)
def method_not_allowed(e="405: Method Not Allowed", json=False):
    return handle_error(e, MethodNotAllowed.code, json)


@errorhandler(Gone.code)
def gone(e="410: Gone", json=False):
    return handle_error(e, Gone.code, json)


@errorhandler(Exception)
@errorhandler(InternalServerError.code)
def internal_error(exce):
    if os.environ["FLASK_CONFIG"] == "development":
        raise exce

    code = hexlify(urandom(4)).decode()
    error(Exception("Code: {}".format(code), exce), exc_info=True)
    text = "500: Something bad has happened\n{}".format(code)

    return handle_error(text, InternalServerError.code)
