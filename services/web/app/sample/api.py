# Copyright (C) 2019  Keiron O'Shea <keo7@aber.ac.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
