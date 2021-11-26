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

from flask import redirect, render_template, url_for, flash, abort, request
from flask_login import login_required, login_user, logout_user, current_user
import requests

from . import auth

from .forms import LoginForm, PasswordChangeForm, UserAccountEditForm
from .models import UserAccount, UserAccountToken

from ..database import db
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
        url_for("api.auth_view_user", id=current_user.id, _external=True),
        headers=get_internal_api_header(),
    )

    if response.status_code == 200:
        return render_template("auth/profile.html", user=response.json()["content"])
    else:
        return abort(response.status_code)


@auth.route("/edit", methods=["GET", "POST"])
def edit():
    response = requests.get(
        url_for("api.auth_view_user", id=current_user.id, _external=True),
        headers=get_internal_api_header(),
    )
    form = UserAccountEditForm()

    if response.status_code == 200:
        if form.validate_on_submit():
            user_information = {
                "title": form.title.data,
                "first_name": form.first_name.data,
                "middle_name": form.middle_name.data,
                "last_name": form.last_name.data,
            }
            edit_response = requests.put(
                url_for("api.auth_edit_user", id=current_user.id, _external=True),
                headers=get_internal_api_header(),
                json=user_information,
            )
            if edit_response.status_code == 200:
                flash("User Edited")
                return redirect(url_for("auth.profile"))
            else:
                return edit_response.content

        form = UserAccountEditForm(data=response.json()["content"])
        return render_template("auth/edit.html", form=form)
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


@auth.route("/user_settings", methods=["GET", "POST"])
def user_settings():
    # response = requests.get(
    #     url_for("api.auth_view_user", id=current_user.id, _external=True),
    #     headers=get_internal_api_header(),
    # )
    user_information = {}
    edit_response = requests.put(
        url_for("api.auth_user_settings", id=current_user.id, _external=True),
        headers=get_internal_api_header(),
        json=user_information,
    )
    if edit_response.status_code == 200:
        flash("User setting updated")
        return edit_response.json()
        #return redirect(url_for("auth.profile"))
    else:
        return edit_response.content



@auth.route("/token", methods=["GET"])
@login_required
def generate_token():
    response = requests.get(
        url_for("api.auth_new_token", _external=True), headers=get_internal_api_header()
    )

    if response.status_code == 200:
        token = response.json()["content"]["token"]

        app_qr_response = requests.post(
            url_for("api.misc_generate_barcode", _external=True),
            json={
                "data": "%s;%s;%s" % (token, current_user.email, request.base_url),
                "type": "qrcode",
            },
        )

        if app_qr_response.status_code == 200:

            return render_template(
                "auth/token.html", token=token, qr_code=app_qr_response.json()["b64"]
            )

    abort(response.status_code)
