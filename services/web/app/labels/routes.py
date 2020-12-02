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
from flask import send_file
from io import BytesIO
import tempfile

TEMPLATES_DIRECTORY = os.environ["TEMPLATES_DIRECTORY"]


@labels.route("/sample/<uuid>")
def sample_label(uuid: str):
    sample_template_dir = os.path.join(TEMPLATES_DIRECTORY, "sample")

    ntf = tempfile.NamedTemporaryFile()
    tmp_fp = ntf.name + ".pdf"

    label_writer = LabelWriter(
        os.path.join(sample_template_dir, "template.html"),
        default_stylesheets=(os.path.join(sample_template_dir, "style.css"),),
    )

    records = [dict(sample_id=uuid, sample_name=uuid)]

    label_writer.write_labels(records, target=tmp_fp)
    return send_file(tmp_fp, as_attachment=False, attachment_filename="label.pdf")
