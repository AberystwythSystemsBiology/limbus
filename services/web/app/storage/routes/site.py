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

from flask import (
    redirect,
    abort,
    render_template,
    url_for,
    session,
    request,
    jsonify,
    flash,
)

from flask_login import current_user, login_required
from .. import storage
import requests
from ...misc import get_internal_api_header
from ..forms import SiteRegistrationForm

@storage.route("/site/LIMBSITE-<id>", methods=["GET"])
@login_required
def view_site(id):
    response = requests.get(
        url_for("api.site_view", id=id, _external=True),
        headers=get_internal_api_header(),
        json={"is_locked": False},
    )

    if response.status_code == 200:
        return render_template(
            "storage/site/view.html", site=response.json()["content"]
        )

    return abort(response.status_code)

@storage.route("/site/LIMBSITE-<id>/delete", methods=["GET", "POST"])
@login_required
def delete_site(id):

    edit_response = requests.put(
        url_for("api.storage_site_delete", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    if edit_response.status_code == 200:
        flash("Site Successfully Deleted")
        return redirect(url_for("storage.index", _external=True))
    # elif edit_response.json()["message"]== "Can't delete assigned samples":
    #     flash("Cannot delete rack with assigned samples")
    else:
        flash("We have a problem: %s" % (id))
    return redirect(url_for("storage.view_site", id=id, _external=True))

@storage.route("/site/LIMBSITE-<id>/edit", methods=["GET", "POST"])
@login_required
def edit_site(id):

    response = requests.get(
        url_for("api.site_view", id=id, _external=True),
        headers=get_internal_api_header(),
    )

    if response.status_code == 200:

        form = SiteRegistrationForm(data=response.json()["content"])

        if form.validate_on_submit():
            form_information = {
                "name": form.name.data,
            }

            edit_response = requests.put(
                url_for("api.storage_site_edit", id=id, _external=True),
                headers=get_internal_api_header(),
                json=form_information,
            )


            if edit_response.status_code == 200:
                flash("Site Successfully Edited")
            else:
                flash("We have a problem: %s" % (edit_response.json()))

            return redirect(url_for("storage.view_site", id=id))
            #return redirect(url_for("storage.view_room", id=id))
            # return redirect(url_for("storage.view_building", id=id)) #DOESNT WORK ID DOESNT REFER TO BUILDING ID


        return render_template(
            "storage/site/edit.html", room=response.json()["content"], form=form
        )

    return abort(response.status_code)

@storage.route("/site/LIMBSITE-<id>/lock", methods=["GET", "POST"])
@login_required
def lock_site(id):

    edit_response = requests.put(
        url_for("api.storage_site_lock", id=id, _external=True),
        headers=get_internal_api_header(),
        #json=form_information,
    )

    if edit_response.status_code == 200:
        if edit_response.json()["content"]:
            flash("Site Successfully Locked")
        else:
            flash("Site Successfully Unlocked")
    else:
        flash("We have a problem: %s" % (edit_response.status_code))

    return redirect(url_for("storage.view_site", id=id))

    #return render_template(
    #    "storage/room/edit.html", room=response.json()["content"], form=form
    #)

    return abort(response.status_code)




