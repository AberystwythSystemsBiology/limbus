from . import admin
from .. import db

from flask import render_template, url_for, redirect, abort
from flask_login import current_user, login_required


from .forms import TemporaryRegistrationForm
from .views import UserAccountsView

from ..auth.models import  User

from functools import wraps


def check_if_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_admin:
            return f(*args, **kwargs)
        return abort(401)

    return decorated_function


@admin.route("/", methods=["GET", "POST"])
@check_if_admin
@login_required
def index():
    form = TemporaryRegistrationForm()

    accounts = UserAccountsView()

    if form.validate_on_submit():


        user = User(
            email=form.email.data,
            password=form.password.data,
            is_admin=form.is_admin.data,
        )
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("admin.index"))

    return render_template("admin/index.html", form=form, accounts=accounts)
