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


import requests
from ...misc import get_internal_api_header
from .. import storage
from flask import render_template, redirect, url_for, abort, flash
from flask_login import current_user, login_required
from ..forms import BuildingRegistrationForm

@storage.route("LIMBSIT/building/new", methods=["GET", "POST"])
@login_required
def new_building():
    form = BuildingRegistrationForm()
    if form.validate_on_submit():
        response = requests.post(
            url_for("api.storage_building_new", _external=True),
            headers=get_internal_api_header(),
            json={
                "site_id": form.site.data,
                "name": form.name.data
            }
        )

        if response.status_code == 200:
            flash("Building Successfully Created")
            return redirect(url_for("storage.index"))
        else:
            return abort(response.status_code)
        
    return render_template("storage/building/new.html", form=form)