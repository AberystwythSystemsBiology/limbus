# API stuff here.

import treepoem

from flask import send_file

from . import sample
from flask_login import login_required

from .views.sample import BasicSampleView

from io import StringIO, BytesIO

from tempfile import NamedTemporaryFile


@sample.route("view/LIMBSMP-<sample_id>/barcode/<attr>")
@login_required
def get_barcode(sample_id: int, attr: str):
    sample = BasicSampleView(sample_id)

    img = treepoem.generate_barcode(barcode_type="qrcode", data=str(sample[attr]))

    img_io = BytesIO()
    img.save(img_io, format="JPEG")
    img_io.seek(0)

    return send_file(img_io, mimetype="image/jpeg")
