# Copyright (C) 2020 Keiron O'Shea <keo7@aber.ac.uk>
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


import requests
from flask import url_for
from wtforms.validators import ValidationError

from .misc import get_internal_api_header


def validate_barcode(form, field):
    if field.data != "":
        samples_response = requests.get(
            url_for("api.sample_query", _external=True),
            headers=get_internal_api_header(),
            json={"barcode": field.data},
        )

        if samples_response.status_code == 200:
            if len(samples_response.json()["content"]) != 0:
                raise ValidationError("Biobank barcode must be unique!")


# TODO: If the Sample disposal != No Disposal, then make sure date has information.
def sample_disposal_date(form, field):
    pass
