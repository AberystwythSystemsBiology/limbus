from flask import redirect, render_template, url_for, flash, abort
from flask_login import login_required, login_user, logout_user, current_user
import requests

from . import auth

from .forms import LoginForm, PasswordChangeForm
from .models import UserAccount, UserAccountToken

from .. import db
from ..misc import get_internal_api_header

from uuid import uuid4

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
        return render_template("auth/profile.html", user=response.json()["content"])
    else:
        return abort(response.status_code)

@auth.route("/change_password", methods=["GET", "POST"])
def change_password():
    form = PasswordChangeForm()

    if form.validate_on_submit():
        if current_user.verify_password(form.current_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash("Password updated")
            return redirect(url_for("auth.profile"))
        else:
            flash("You have entered in the wrong current password, try again.")
            return redirect(url_for("auth.change_password"))

    return render_template("auth/password.html", form=form)


@auth.route("/token", methods=["GET"])
@login_required
def generate_token():
    # I was going to make this API based, but I'd rather the user log in just in-case :)
    new_token = str(uuid4())

    uat = UserAccountToken.query.filter_by(user_id = current_user.id).first()
    if uat != None:
        uat.token = new_token
    else:
        uat = UserAccountToken(
            user_id = current_user.id,
            token = new_token
        )

    db.session.add(uat)
    db.session.commit()

    return render_template("auth/token.html", token=new_token)