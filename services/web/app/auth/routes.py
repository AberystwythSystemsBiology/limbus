from flask import redirect, render_template, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user


from . import auth

from .forms import LoginForm, ChangePassword
from .models import UserAccount

from .views import UserView

from .. import db


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = db.session.query(UserAccount).filter(UserAccount.email == form.email.data).first()
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
    user = UserView(current_user.id)

    password_change = ChangePassword()

    return render_template(
        "auth/profile.html", user=user, password_change=password_change
    )
