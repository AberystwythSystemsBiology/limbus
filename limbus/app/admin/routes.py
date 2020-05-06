from . import admin
from .. import db

from flask import render_template, url_for, redirect, abort
from flask_login import current_user

from .forms import TemporaryRegistrationForm
from .views import UserAccountsView

from ..auth.models import Profile, User

from functools import wraps

def check_if_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_admin:
            return f(*args, **kwargs)
        return abort(401)
    return decorated_function

@admin.route("/", methods=["GET", "POST"])
@check_if_admin
def index():
    form = TemporaryRegistrationForm()

    accounts = UserAccountsView()

    if form.validate_on_submit():
        
        profile = Profile(
            title=form.title.data,
            first_name=form.first_name.data,
            middle_name=form.middle_name.data,
            last_name=form.last_name.data,
        )

        db.session.add(profile)
        db.session.flush()

        user = User(email=form.email.data, password=form.password.data, is_admin=False, profile_id=profile.id)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("admin.index"))

    return render_template("admin/index.html", form=form, accounts=accounts)