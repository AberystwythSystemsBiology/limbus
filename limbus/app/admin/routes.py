from . import admin
from .. import db

from flask import render_template

from .forms import TemporaryRegistrationForm
from .views import UserAccountsView

@admin.route("/", methods=["GET", "POST"])
def index():
    form = TemporaryRegistrationForm()

    accounts = UserAccountsView()

    if form.validate_on_submit():
        return "Submitted"
    return render_template("admin/index.html", form=form, accounts=accounts)