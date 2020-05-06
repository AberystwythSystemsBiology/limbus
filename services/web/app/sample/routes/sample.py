from .. import sample
from flask import render_template
from flask_login import login_required

from ..views.sample import SampleView


@sample.route("view/LIMBSMP-<sample_id>")
@login_required
def view(sample_id: int):
    sample = SampleView(sample_id)

    return render_template("sample/sample/view.html", sample=sample)
