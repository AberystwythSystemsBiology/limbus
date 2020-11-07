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

from flask_login import current_user, login_required

from ..forms import LongTermColdStorageForm, NewShelfForm

@storage.route("/coldstorage/new", methods=["GET", "POST"])
@login_required
def new_cold_storage()

@storage.route("/coldstorage/LIMBCS-<id>/add_shelf", methods=["GET", "POST"])
@login_required
def add_shelf(id: int):
    pass
    #return render_template("/storage/shelf/new.html", form=form, lts=lts)


@storage.route("/coldstorage/LIMBLTS-<lts_id>/edit", methods=["GET", "POST"])
@login_required
def edit_lts(lts_id):
    pass
