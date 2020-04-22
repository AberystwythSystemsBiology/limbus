from .. import sample

from flask import render_template, redirect, session, url_for, request, jsonify
from flask_login import login_required, current_user

from ... import db
from ..forms import SampleAliquotingForm
from ..models import *

from ..views.sample import SampleView

@sample.route("view/LIMBSMP-<sample_id>/aliquot", methods=["GET", "POST"])
@login_required
def aliquot(sample_id):
    sample = SampleView(sample_id).get_attributes()

    if sample["sample_type"] == SampleType.MOL:
        sample_type = SampleToMolecularSampleType
    elif sample["sample_type"] == SampleType.FLU:
        sample_type = SampleToFluidSampleType
    else:
        sample_type = SampleToCellSampleType

    sample_type = (
        db.session.query(sample_type).filter(sample_type.sample_id == sample_id).first_or_404()
    )

    form = SampleAliquotingForm(sample["sample_type"], sample_type.sample_type)

    if form.validate_on_submit():

        counts = form.count.data
        size = form.size.data
        aliquot_date = form.aliquot_date.data
        aliquot_time = form.aliquot_time.data
        selected_sample_type = form.sample_type.data

        lock_parent = form.lock_parent.data

        for i in range(counts):
            # Create Sample
            a_s = Sample(
                sample_type = sample["sample_type"],
                creation_date = aliquot_date,
                collection_date = aliquot_time,
                quantity = size,
                current_quantity = size,
                disposal_date = sample["disposal_date"],
                author_id = current_user.id
            )

            db.session.add(a_s)
            db.session.flush()

            # Sample Type
            if sample["sample_type"] == SampleType.MOL:
                s_sample_type = SampleToMolecularSampleType
            elif sample["sample_type"] == SampleType.FLU:
                s_sample_type = SampleToFluidSampleType
            else:
                s_sample_type = SampleToCellSampleType

            sst = s_sample_type(
                sample_id = a_s.id,
                sample_type = selected_sample_type,
                author_id = current_user.id
            )

            db.session.add(sst)
            db.session.flush()

            # Add SubSample
            s_ss = SubSampleToSample(
                parent_sample = sample_id,
                author_id = current_user.id
            )

            db.session.add(s_ss)
            db.session.commit()

        sample.db_sessions["sample"].current_quantity = size * counts

        if lock_parent:
            sample.db_sessions["sample"].is_closed = True

        db.session.add(sample.db_sessions)
        db.session.commit()

        return redirect(url_for("sample.view", sample_id=sample_id))

    return render_template("sample/sample/aliquot/create.html", sample=sample, sample_type=sample_type, form=form)
