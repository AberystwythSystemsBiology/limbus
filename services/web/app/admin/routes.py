# Copyright (C) 2019  Keiron O'Shea <keo7@aber.ac.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from . import admin
from .. import db

from flask import render_template, url_for, redirect, abort
from flask_login import current_user, login_required


from .forms import TemporaryRegistrationForm
from .views import UserAccountsView

from ..auth.models import User

from functools import wraps


from ..decorators import check_if_admin


@admin.route("/", methods=["GET", "POST"])
@check_if_admin
@login_required
def index():
    form = TemporaryRegistrationForm()

    accounts = UserAccountsView()

    if form.validate_on_submit():

        user = User(
            email=form.email.data,
            password=form.password.data,
            is_admin=form.is_admin.data,
        )
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("admin.index"))

    return render_template("admin/index.html", form=form, accounts=accounts)
