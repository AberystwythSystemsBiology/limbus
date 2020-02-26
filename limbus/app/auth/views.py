from flask import redirect, render_template, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user

from . import auth

from .forms import LoginForm, ChangePassword
from .models import User, Profile, ProfileToUser

from .. import db


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = db.session.query(User).filter(User.email == form.email.data).first()
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
def profile():
    user = db.session.query(User).filter(User.id == current_user.id).first_or_404()
    profile, _ = (
        db.session.query(Profile, ProfileToUser)
        .filter(ProfileToUser.user_id == current_user.id)
        .filter(ProfileToUser.profile_id == Profile.id)
        .first_or_404()
    )

    password_change = ChangePassword()

    return render_template(
        "auth/profile.html", user=user, profile=profile, password_change=password_change
    )
