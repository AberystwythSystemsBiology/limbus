# Copyright (C) 2021 Keiron O'Shea <keo7@aber.ac.uk>
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

from .. import admin
from ...decorators import check_if_admin
from ...misc import get_internal_api_header

from ...auth.forms import UserAccountRegistrationForm
from ..forms import AccountLockForm

from flask import render_template, url_for, redirect, abort, flash
from flask_login import current_user, login_required

import requests


@admin.route("/sites/", methods=["GET"])
@check_if_admin
@login_required
def sites_index():
    return render_template("admin/sites/index.html")

@admin.route("/sites/new", methods=["GET", "POST"])
@check_if_admin
@login_required
def sites_new_site():
    return "Hello World"