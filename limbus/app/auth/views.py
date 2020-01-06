from flask import redirect, render_template, url_for, flash
from flask_login import login_required, login_user, logout_user

from . import auth
from .. import db
from .forms import LoginForm
from .models import User

@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
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