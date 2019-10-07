from functools import wraps

from flask import redirect, abort, render_template, url_for

from ..auth.models import User

from . import setup
from .. import db
from .forms import BiobankRegistrationForm
from ..auth.forms import RegistrationForm

from random import shuffle

def check_if_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if User.query.first():
            return abort(401)
        return f(*args, **kwargs)
    return decorated_function

@setup.route("/")
@check_if_user
def index():
    # Step One: Provide the user with instructions.
    return render_template("setup/index.html")

@setup.route("/eula")
@check_if_user
def eula():
    # Step Two: Present the EULA.
    return render_template("setup/eula.html")

@setup.route("/admin_registration", methods=["GET", "POST"])
@check_if_user
def admin_registration():
    # Step Three: Ask the user to register themselves as administrator.
    form=RegistrationForm()
    if form.validate_on_submit():
        admin = User(
            email = form.email.data,
            first_name = form.first_name.data,
            last_name = form.last_name.data,
            password = form.password.data,
            is_admin=True
        )
        db.session.add(admin)

        db.session.commit()

        return redirect(url_for("setup.biobank_registration"))

        
    return render_template("setup/admin_registration.html", form=form)

@setup.route("/biobank_registration", methods=["GET", "POST"])
def biobank_registration():

    def _generate_acronym(cc: str, bn: str) -> str:
        bn = [x for x in list(bn) if x != " "]
        shuffle(bn)
        return "%s_%s" % (cc, "".join(bn[0:7]))

    # Step Four: Ask the user to register the biobank's information

    form = BiobankRegistrationForm()

    if form.validate_on_submit():
        _generate_acronym(form.country.data, form.name.data)


        #return redirect("misc.index")

    return render_template("setup/biobank_registration.html", form=form)