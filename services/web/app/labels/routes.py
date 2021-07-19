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

from . import labels

from blabel import LabelWriter
import os
from flask import send_file, url_for
from io import BytesIO
import tempfile
from flask_login import login_required
from ..misc import get_internal_api_header
import requests

TEMPLATES_DIRECTORY = os.environ["TEMPLATES_DIRECTORY"]


@labels.route("/sample/<uuid>")
@login_required
def sample_label(uuid: str):
    sample_template_dir = os.path.join(TEMPLATES_DIRECTORY, "sample")

    sample_response = requests.get(
        url_for("api.sample_view_sample", uuid=uuid, _external=True),
        headers=get_internal_api_header(),
    )

    if sample_response.status_code == 200:
        ntf = tempfile.NamedTemporaryFile()
        tmp_fp = ntf.name + ".pdf"

        label_writer = LabelWriter(
            os.path.join(sample_template_dir, "template.html"),
            default_stylesheets=(os.path.join(sample_template_dir, "style.css"),),
        )

        sample = sample_response.json()["content"]
        print('sample', sample)
        base_type = sample["base_type"]

        if base_type == "Fluid":
            measurement = "mL"
            sample_type = sample["sample_type_information"]["fluid_type"];

        elif base_type == "Cell":
            measurement = "Cells"
            sample_type = sample["sample_type_information"]["cellular_type"];

        elif base_type == "Molecular":
            measurement = "μg/mL"
            sample_type = sample["sample_type_information"]["molecular_type"];

        records = [
            dict(
                sample_id=sample["uuid"],
                sample_name=sample["uuid"],
                #sample_type=sample["base_type"],
                sample_type=sample_type,
                measurement=measurement,
                sample_quantity=sample["remaining_quantity"],
            )
        ]

        label_writer.write_labels(records, target=tmp_fp)
        return send_file(tmp_fp, as_attachment=False, attachment_filename="label.pdf")

    return abort(sample_response.status_code)
