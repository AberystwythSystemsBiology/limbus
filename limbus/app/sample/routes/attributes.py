from .. import sample
from flask import render_template
from flask_login import login_required
from ... import db



@sample.route("attribute/")
@login_required
def attribute_portal():
    sample_attributes = []
    return render_template(
        "sample/attribute/index.html", sample_attributes=sample_attributes
    )