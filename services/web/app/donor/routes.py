from . import donor
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from .models import Donors
from .forms import DonorCreationForm
from .views import DonorIndexView, DonorView

from .. import db


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
            age = form.age.data,
            sex = form.sex.data,
            status = form.status.data,
            race = form.race.data,
            death_date = death_date,
            weight = form.weight.data,
            height = form.height.data,
            author_id = current_user.id
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
        donor_obj.age = form.age.data
        donor_obj.sex = form.sex.data
        donor_obj.weight = form.weight.data
        donor_obj.height = form.height.data
        donor_obj.race = form.race.data
        donor_obj.status = form.status.data

        db.session.commit()
        flash("Donor information successfully edited!")
        return redirect(url_for("donor.view",donor_id=donor_id))

    return render_template("donor/edit.html", form=form, donor_id=donor_id)
