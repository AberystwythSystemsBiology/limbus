from flask import render_template, redirect, session, url_for, request, jsonify
from .. import sample
from flask_login import login_required, current_user
from ... import db
from ..forms import SampleAliquotingForm
from ..enums import CellSampleType, MolecularSampleType, FluidSampleType
from ..models import *

@sample.route("view/LIMBSMP-<sample_id>/aliquot", methods=["GET", "POST"])
@login_required
def aliquot(sample_id):
    sample = (
        db.session.query(Sample)
            .filter(Sample.id == sample_id)
            .first_or_404()
    )

    if sample.sample_type == SampleType.MOL:
        sample_type = SampleToMolecularSampleType
    elif sample.sample_type == SampleType.FLU:
        sample_type = SampleToFluidSampleType
    else:
        sample_type = SampleToCellSampleType

    sample_type = (
        db.session.query(sample_type).filter(sample_type.sample_id == sample_id).first_or_404()
    )

    form = SampleAliquotingForm(sample.sample_type, sample_type.sample_type)

    if form.validate_on_submit():

        counts = form.count.data
        size = form.size.data
        aliquot_date = form.aliquot_date.data
        aliquot_time = form.aliquot_time.data

        lock_parent = form.lock_parent.data

        for i in range(counts):
            # Create Sample
            a_s = Sample()

            # Sample Type

            # Add SubSample
            s_ss = SubSampleToSample()

            # Update Sample to reflect quantity change.
            #sample



    return render_template("sample/sample/aliquot/create.html", sample=sample, sample_type=sample_type, form=form)
