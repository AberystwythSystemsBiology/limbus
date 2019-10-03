from functools import wraps

from flask import redirect, abort, render_template, url_for

from ..auth.models import User

from . import setup
from .. import db
from ..auth.forms import RegistrationForm

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
    return render_template("setup/index.html")

@setup.route("/eula")
@check_if_user
def eula():
    return render_template("setup/eula.html")

@setup.route("/admin_registration", methods=["GET", "POST"])
@check_if_user
def admin_registration():
    form=RegistrationForm()
    if form.validate_on_submit():
        # Add the User account here.
        pass
    return render_template("setup/admin_registration.html", form=form)