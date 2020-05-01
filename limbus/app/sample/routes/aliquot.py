from .. import sample as s_bp

from copy import deepcopy

from flask import render_template, redirect, session, url_for, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy.orm.session import make_transient

from ... import db
from ..forms import SampleAliquotingForm
from ..models import *

from ..views.sample import SampleView

@s_bp.route("view/LIMBSMP-<sample_id>/aliquot", methods=["GET", "POST"])
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

    form, num_processing_templates = SampleAliquotingForm(sample_attributes["sample_type"], sample_type.sample_type)

    if form.validate_on_submit():

        counts = form.count.data
        size = form.size.data
        aliquot_date = form.aliquot_date.data
        aliquot_time = form.aliquot_time.data.strftime("%H:%M:%S")
        selected_sample_type = form.sample_type.data
        processing_template = form.processing_template.data

        lock_parent = form.lock_parent.data

        for i in range(counts):

            sample_cpy = db.session.query(Sample).filter(Sample.id == sample_id).first_or_404()

            db.session.expunge(sample_cpy)
            make_transient(sample_cpy)

            sample_cpy.id = None
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

            spcfta = SamplePatientConsentFormTemplateAssociation(
                sample_id=sample_cpy.id,
                template_id=sample_attributes["consent_info"]["id"],
                consent_id=sample_attributes["consent_info"]["association_id"],
                author_id=current_user.id,
            )

            db.session.add(spcfta)
            db.session.flush()

            spta = SampleProcessingTemplateAssociation(
                sample_id=sample_cpy.id,
                template_id=processing_template,
                processing_time=aliquot_time,
                processing_date=aliquot_date,
                author_id=current_user.id,
            )

            db.session.add(spta)
            db.session.flush()

            # Add SubSample
            s_ss = SubSampleToSample(
                parent_sample_id = sample_id,
                subsample_sample_id = sample_cpy.id,
                author_id = current_user.id
            )

            db.session.add(s_ss)
            db.session.commit()

        sample_cpy = db.session.query(Sample).filter(Sample.id == sample_id).first_or_404()



        sample_cpy.current_quantity = float(sample_cpy.current_quantity) - (float(size) * float(counts))

        if lock_parent:
            sample_cpy.is_closed = True

        db.session.add(sample_cpy)
        db.session.commit()

        return redirect(url_for("sample.view", sample_id=sample_id))

    return render_template("sample/sample/aliquot/create.html",
                           sample=sample_attributes,
                           sample_type=sample_type,
                           form=form,
                           num_processing_templates=num_processing_templates
                           )
