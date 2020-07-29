import requests
import json

from flask import redirect, abort, render_template, url_for, session, flash, current_app, jsonify
from flask_login import logout_user, current_user


from ..auth.forms import UserAccountRegistrationForm

from . import setup
from .forms import SiteRegistrationForm

from ..decorators import as_kryten, setup_mode

from ..generators import generate_random_hash

from ..misc import get_internal_api_header, clear_session


@setup.route("/")
@as_kryten
@setup_mode
def index():
    return render_template("setup/index.html")


@setup.route("/eula")
@setup_mode
def eula():
    return render_template("setup/eula.html")


@setup.route("/site_registration", methods=["GET", "POST"])
@as_kryten
@setup_mode
def site_registration():
    form = SiteRegistrationForm()
    if form.validate_on_submit():
        hash = generate_random_hash()
        site = {
            "name": form.name.data,
            "url": form.url.data,
            "description": form.description.data
        }

        address = {
                "street_address_one": form.address_line_one.data,
                "street_address_two": form.address_line_two.data,
                "city": form.city.data,
                "country": form.country.data,
                "post_code": form.post_code.data
        }

        session[hash] = {"site": site, "address": address}
        return redirect(url_for("setup.admin_registration", hash=hash))

    return render_template("setup/site_registration.html", form=form)


@setup.route("/test", methods=["GET", "POST"])
@as_kryten
def test():
    
    test_address = {
        "street_address_one": "10 Downing Street",
        "city": "London",
        "country": "GB",
        "post_code": "SW1A2AA",
    }

    test_site = {
        "name": "Aberystwyyth Systems Biology",
        "url": "http://www.aber.ac.uk/en",
        "address_id": 1
    }

    r = requests.post(url_for("api.misc_new_site", _external=True), json=test_site, headers=get_internal_api_header())

    if r.status_code == 200:
        logout_user()
        return r.json()
    else:
        return r.content

@setup.route("/administrator_registration/<hash>", methods=["GET", "POST"])
@as_kryten
@setup_mode
def admin_registration(hash: str):
    # Step Three: Ask the user to register themselves as administrator.
    form = UserAccountRegistrationForm()
    if form.validate_on_submit():

        site_information = session[hash]["site"]
        site_address = session[hash]["address"]

        new_address_request = requests.post(
            url_for("api.misc_new_address", _external=True), json=site_address, headers=get_internal_api_header()
        )

        if new_address_request.status_code == 200:
            site_information["address_id"] = json.loads(new_address_request.json()["content"])["id"]
        else:
            return abort(new_address_request.status_code)

        new_site_request = requests.post(
            url_for("api.misc_new_site", _external=True), json=site_information, headers=get_internal_api_header()
        )

        if new_site_request.status_code == 200:
            user_account = {
                "title": form.title.data,
                "first_name": form.first_name.data,
                "middle_name": form.middle_name.data,
                "last_name": form.last_name.data,
                "email": form.email.data,
                "account_type": "ADM",
                "password": form.password.data,
                "site_id": json.loads(new_site_request.json()["content"])["id"]
            }
        else:
            return abort(new_address_request.status_code)


        new_user_request = requests.post(
            url_for("api.auth_new_user", _external=True), json=user_account, headers=get_internal_api_header()
            )

        if new_user_request.status_code == 200:

            logout_user()
            clear_session(hash)
            return redirect(url_for("setup.complete"))
        if new_user_request.status_code == 400:
            return new_user_request.content
        else:
            return new_user_request.content

        return new_address_request
    return render_template("setup/admin_registration.html", form=form, hash=hash)


@setup.route("/complete")
def complete():
    return render_template("setup/complete.html")
