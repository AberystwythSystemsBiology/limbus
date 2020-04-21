from flask import render_template

from .. import sample
from flask_login import login_required
from ... import db

from ..models import Sample, SampleAttribute

from ...auth.models import User


@sample.route("/")
@login_required
def sap_portal():
    info = {
        "sample_count": db.session.query(Sample).count(),
        "sample_attr_count": db.session.query(SampleAttribute).count(),
        "donor_count": 0,
    }

    return render_template("sample/index.html", info=info)
