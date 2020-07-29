from flask import redirect, render_template, url_for, flash, abort
from flask_login import login_required, login_user, logout_user, current_user
import requests

from . import auth

from .forms import LoginForm, ChangePassword
from .models import UserAccount

from .. import db
from ..misc import get_internal_api_header

@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = (
            db.session.query(UserAccount)
            .filter(UserAccount.email == form.email.data)
            .first()
        )
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            flash("Successfuly logged in.")
            return redirect(url_for("misc.index"))
        else:
            flash("Incorrect email or password.")
    return render_template("auth/login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have successfully been logged out.")
    return redirect(url_for("auth.login"))


@auth.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    response = requests.get(
        url_for("api.auth_view_user", id=current_user.id, _external=True, headers=get_internal_api_header())
    )

    if response.status_code == 200:
        password_change = ChangePassword()
        return render_template("auth/profile.html", user=response.json()["content"], password_change=password_change)
    else:
        return abort(response.status_code)

