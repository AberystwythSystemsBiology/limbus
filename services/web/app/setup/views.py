from functools import wraps

from flask import redirect, abort, render_template, url_for, session

from ..auth.models import UserAccount
from ..misc.models import SiteInformation, Address

from . import setup
from .. import db
from .forms import SiteRegistrationForm

from ..decorators import check_if_user

from ..generators import generate_random_hash


@setup.route("/")
@check_if_user
def index():
    return render_template("setup/index.html")


@setup.route("/eula")
@check_if_user
def eula():
    return render_template("setup/eula.html")

@setup.route("/site_registration", methods=["GET", "POST"])
def site_registration():

    form = SiteRegistrationForm()

    if form.validate_on_submit():

        site = {
            "name": form.name.data,
            "url": form.url.data,
            "description": form.description.data,
            "address" : {
                "street_address_one": form.address_line_one.data,
                "street_address_two": form.address_line_two.data,
                "city": form.city.data,
                "country":  form.country.data,
                "post_code": form.post_code.data,
            }
        }




        return redirect(url_for("setup.complete"))

    return render_template("setup/site_registration.html", form=form)


# TODO: Register site first.

@setup.route("/register_admin", methods=["GET", "POST"])
@check_if_user
def admin_registration():
    # Step Three: Ask the user to register themselves as administrator.
    form = BiobankRegistrationForm()


    return render_template("setup/admin_registration.html", form=form)




@setup.route("/complete")
def complete():
    return render_template("setup/complete.html")
