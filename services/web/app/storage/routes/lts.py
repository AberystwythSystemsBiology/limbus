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

from .. import storage
import requests
from ...misc import get_internal_api_header
from flask_login import current_user, login_required

from ..forms import ColdStorageForm, NewShelfForm

@storage.route("/coldstorage/new/LIMROOM-<id>", methods=["GET", "POST"])
@login_required
def new_cold_storage(id):
    
    response = requests.get(
        url_for("api.storage_room_view", id=id, _external=True),
        headers=get_internal_api_header()
    )



    if response.status_code == 200:
        form = ColdStorageForm()

        if form.validate_on_submit():
            new_response = requests.post(
                url_for("api.storage_coldstorage_new", _external=True),
                headers=get_internal_api_header(),
                json={
                    "room_id": id,
                    "serial_number": form.serial_number.data,
                    "manufacturer": form.manufacturer.data,
                    "comments": form.comments.data,
                    "temp": form.temperature.data,
                    "type": form.type.data
                }
            )

            if new_response.status_code == 200:
                flash("Cold Storage Successfuly Created")
                # TODO: Replace
                return redirect(url_for("storage.view_cold_storage", id=new_response.json()["content"]["id"]))
            return abort(new_response.status_code)

        return render_template("storage/lts/new.html", form=form, room=response.json()["content"])


    else:
        abort(response.status_code)


@storage.route("/coldstorage/LIMBCS-<id>", methods=["GET"])
@login_required
def view_cold_storage(id):
    response = requests.get(
        url_for("api.storage_coldstorage_view", id=id, _external=True),
        headers=get_internal_api_header()
    )

    if response.status_code == 200:
        return render_template("storage/lts/view.html", cs=response.json()["content"])
    return abort(response.status_code)

    '''
    if response.status_code == 200:
        return render_template("storage/room/view.html", room=response.json()["content"])

    return abort(response.status_code)
    '''



@storage.route("/coldstorage/LIMBLTS-<lts_id>/edit", methods=["GET", "POST"])
@login_required
def edit_lts(lts_id):
    pass
