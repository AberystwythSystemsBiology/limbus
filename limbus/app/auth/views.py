from flask import redirect, render_template, url_for
from flask_login import login_required, login_user, logout_user

from . import auth
from .. import db
from .forms import LoginForm
from .models import User

@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        pass
    return render_template("auth/login.html", form=form)