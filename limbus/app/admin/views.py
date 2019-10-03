from functools import wraps

from flask import redirect, render_template, url_for, flash, abort
from flask_login import login_required, login_user, logout_user, current_user

from . import admin
from .. import db

def check_if_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            return abort(401)
        return f(*args, **kwargs)
    return decorated_function

@admin.route("/")
@login_required # Not sure if redundant due to @check_if_admin
@check_if_admin
def admin_panel():
    return "Hello World"