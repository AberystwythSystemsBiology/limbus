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

    if sample.sample_type == "Molecular":
        sample_type = SampleToMolecularSampleType
    elif sample.sample_type == "Fluid":
        sample_type = SampleToFluidSampleType
    else:
        sample_type = SampleToCellSampleType

    sample_type = (
        db.session.query(sample_type).filter(sample_type.sample_id == sample_id).first_or_404()
    )
    form = SampleAliquotingForm(sample.sample_type, sample_type.sample_type)

    return render_template("sample/sample/aliquot/create.html", sample=sample, form=form)
