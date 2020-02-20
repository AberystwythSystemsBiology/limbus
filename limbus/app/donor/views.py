from flask import render_template, redirect, url_for
from . import donor
from .models import Donor, DonorDiagnosticProcedureInformation, DonorVisitNumber
from .forms import DonorCreationForm
from flask_login import login_required, current_user

from .. import db


@donor.route("/")
def index():
    donors = db.session.query(Donor).all()
    return render_template("donor/index.html", donors=donors)


@donor.route("/add", methods=["GET", "POST"])
def add_donor():
    form = DonorCreationForm()

    if form.validate_on_submit():
        donor = Donor(
            age=form.age.data,
            height=form.height.data,
            sex=form.sex.data,
            author_id=current_user.id,
        )

        db.session.add(donor)
        db.session.commit()

        return redirect(url_for("donor.index"))

    return render_template("donor/information/add.html", form=form)
