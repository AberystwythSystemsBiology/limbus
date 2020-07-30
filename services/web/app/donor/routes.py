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

from . import donor
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from .models import Donors
from .forms import DonorCreationForm
from .views import DonorIndexView, DonorView

from .. import db

import uuid


@login_required
@donor.route("/")
def index():
    donors = DonorIndexView()
    return render_template("donor/index.html", donors=donors)


@login_required
@donor.route("/add", methods=["GET", "POST"])
def add():
    form = DonorCreationForm()
    if form.validate_on_submit():

        death_date = None
        if form.status.data == "DE":
            death_date = form.death_date.data

        donor = Donors(
            uuid=uuid.uuid4(),
            age=form.age.data,
            sex=form.sex.data,
            status=form.status.data,
            race=form.race.data,
            death_date=death_date,
            weight=form.weight.data,
            height=form.height.data,
            author_id=current_user.id,
        )

        db.session.add(donor)
        db.session.commit()

        flash("Donor information successfully added!")
        return redirect(url_for("donor.index"))

    return render_template("donor/add.html", form=form)


@login_required
@donor.route("/view/LIMBDON-<donor_id>")
def view(donor_id):
    donor = DonorView(donor_id)
    return render_template("donor/view.html", donor=donor)


@login_required
@donor.route("/edit/LIMBDON-<donor_id>", methods=["GET", "POST"])
def edit(donor_id):
    donor_obj = db.session.query(Donors).filter(Donors.id == donor_id).first_or_404()
    form = DonorCreationForm(obj=donor_obj)

    if form.validate_on_submit():

        death_date = None

        if form.status.data == "DE":
            death_date = form.death_date.data

        donor_obj.age = form.age.data
        donor_obj.sex = form.sex.data
        donor_obj.weight = form.weight.data
        donor_obj.height = form.height.data
        donor_obj.race = form.race.data
        donor_obj.status = form.status.data
        donor_obj.updater_id = current_user.id
        donor_obj.death_date = death_date

        db.session.commit()
        flash("Donor information successfully edited!")
        return redirect(url_for("donor.view", donor_id=donor_id))

    return render_template("donor/edit.html", form=form, donor_id=donor_id)
