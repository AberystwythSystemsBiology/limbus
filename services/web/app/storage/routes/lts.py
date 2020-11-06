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

# from ... import db
from .. import storage

from ..forms import LongTermColdStorageForm, NewShelfForm

# from ..models import FixedColdStorageShelf, FixedColdStorage

from uuid import uuid4

# from ..views import LTSView, BasicLTSView


@storage.route("/lts/LIMBLTS-<lts_id>", methods=["GET"])
@login_required
def view_lts(lts_id: int):
    # lts = LTSView(lts_id)
    return render_template("/storage/lts/view.html", lts=None)


"""

@storage.route("/lts/LIMBLTS-<lts_id>/add_shelf", methods=["GET", "POST"])
@login_required
def add_shelf(lts_id: int):
    lts = BasicLTSView(lts_id)

    form = NewShelfForm()

    if form.validate_on_submit():
        shelf = FixedColdStorageShelf(
            name=form.name.data,
            # Generate an UUID :)
            uuid=uuid4(),
            description=form.description.data,
            storage_id=lts_id,
            author_id=current_user.id,
        )

        db.session.add(shelf)
        db.session.commit()

        return redirect(url_for("storage.view_lts", lts_id=lts_id))

    return render_template("/storage/shelf/new.html", form=form, lts=lts)


@storage.route("/lts/LIMBLTS-<lts_id>/edit", methods=["GET", "POST"])
@login_required
def edit_lts(lts_id):
    lts = LTSView(lts_id)
    form = LongTermColdStorageForm()

    if form.validate_on_submit():
        s = (
            db.session.query(FixedColdStorage)
            .filter(FixedColdStorage.id == lts_id)
            .first_or_404()
        )
        s.manufacturer = form.manufacturer.data
        # TODO: Fix this annoying issue wherein forms aren't being validated against enumerated types properly.
        # s.temperature = form.temperature.data,
        s.serial_number = (form.serial_number.data,)
        s.type = form.type.data

        s.author_id = current_user.id

        db.session.commit()
        flash("Successfully edited!")
        return redirect(url_for("storage.view_lts", lts_id=lts_id))

    form.manufacturer.data = lts["manufacturer"]
    form.temperature.data = lts["temperature"]
    form.serial_number.data = lts["serial_number"]
    form.type.data = lts["type"]

    return render_template("storage/lts/edit.html", lts=lts, form=form)

"""
