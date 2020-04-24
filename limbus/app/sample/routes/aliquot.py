from .. import sample

from copy import deepcopy

from flask import render_template, redirect, session, url_for, request, jsonify
from flask_login import login_required, current_user

from ... import db
from ..forms import SampleAliquotingForm
from ..models import *

from ..views.sample import SampleView

@sample.route("view/LIMBSMP-<sample_id>/aliquot", methods=["GET", "POST"])
@login_required
def aliquot(sample_id):
    s = SampleView(sample_id)

    sample_attributes = s.get_attributes()

    if sample_attributes["sample_type"] == SampleType.MOL:
        sample_type = SampleToMolecularSampleType
    elif sample_attributes["sample_type"] == SampleType.FLU:
        sample_type = SampleToFluidSampleType
    else:
        sample_type = SampleToCellSampleType

    sample_type = (
        db.session.query(sample_type).filter(sample_type.sample_id == sample_id).first_or_404()
    )

    form, num_processing_templates = SampleAliquotingForm(sample["sample_type"], sample_type.sample_type)

    if form.validate_on_submit():

        counts = form.count.data
        size = form.size.data
        aliquot_date = form.aliquot_date.data
        selected_sample_type = form.sample_type.data
        processing_template = form.processing_template.data

        lock_parent = form.lock_parent.data

        for i in range(counts):

            sample_cpy = deepcopy(s.db_sessions["sample"])

            db.session.expunge(sample_cpy)
            db.session.make_transient(sample_cpy)

            sample_cpy.biobank_barcode = None
            sample_cpy.quantity = size
            sample_cpy.current_quantity = size
            sample_cpy.author_id = current_user.id
            sample_cpy.collection_date = aliquot_date

            db.session.add(sample_cpy)

            db.session.flush()

            # Sample Type
            if sample_cpy.sample_type == SampleType.MOL:
                s_sample_type = SampleToMolecularSampleType
            elif sample_cpy.sample_type == SampleType.FLU:
                s_sample_type = SampleToFluidSampleType
            else:
                s_sample_type = SampleToCellSampleType

            sst = s_sample_type(
                sample_id = sample_cpy.id,
                sample_type = selected_sample_type,
                author_id = current_user.id
            )

            db.session.add(sst)
            db.session.flush()

            # Protocol and Consent from form and parent.



            # Add SubSample
            s_ss = SubSampleToSample(
                parent_sample = sample_id,
                subsample_sample_id = sample_cpy.id,
                author_id = current_user.id
            )

            db.session.add(s_ss)
            db.session.commit()




        s.db_sessions["sample"].current_quantity = size * counts

        if lock_parent:
            s.db_sessions["sample"].is_closed = True

        db.session.add(s.db_sessions["sample"])
        db.session.commit()

        return redirect(url_for("sample.view", sample_id=sample_id))

        return processing_template
        '''
        return "Hello Kitty"

    return render_template("sample/sample/aliquot/create.html",
                           sample=sample,
                           sample_type=sample_type,
                           form=form,
                           num_processing_templates=num_processing_templates
                           )
