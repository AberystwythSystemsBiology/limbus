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


from flask_wtf import FlaskForm
from flask import render_template, redirect, session, url_for, flash, abort
from ...misc import get_internal_api_header
import requests
from wtforms import SelectField, StringField, SubmitField, BooleanField, SelectMultipleField
from ..enums import Colour, BiohazardLevel, SampleSource, SampleStatus, SampleBaseType
from ...consent.enums import QuestionType

def SampleFilterForm(sites: list, sampletypes: list, data: {}) -> FlaskForm:
    sampletypes.insert(0, (None, "None"))
    print("sampletype", sampletypes)
    class StaticForm(FlaskForm):
        biohazard_level = SelectField(
            "Biohazard Level", choices=BiohazardLevel.choices(with_none=True)
        )

        uuid = StringField("UUID")
        barcode = StringField("Barcode")
        colour = SelectField("Colour", choices=Colour.choices(with_none=True))
        base_type = SelectField("Base Type", choices=SampleBaseType.choices(with_none=True))
        source = SelectField("Sample Source", choices=SampleSource.choices(with_none=True))
        status = SelectField("Sample Status", choices=SampleStatus.choices(with_none=True))

        submit = SubmitField("Filter")

    setattr(
        StaticForm,
        "sample_type",
        SelectField(
            "Sample Type", choices=sampletypes,
            default=None
        ),
    )

    setattr(
        StaticForm,
        "current_site_id",
        SelectField(
            "Site", choices=sites,
            default=None
        ),
    )

    setattr(
        StaticForm,
        "consent_status",
        SelectField(
            "Consent status", choices=[(None, "None"), ("active", "Active"), ("withdrawn", "Withdrawn")],
            default=None
        ),
    )

    setattr(
        StaticForm,
        "consent_type",
        SelectMultipleField(
            "Consent type", choices=QuestionType.choices(), #(with_none=True),
        ),
    )

    # Get protocol template list
    protocols_response = requests.get(
        url_for("api.protocol_query", _external=True),
        headers=get_internal_api_header(),
        json={"is_locked": False},
    )

    protocols = [(None, "None")]
    if protocols_response.status_code == 200:
        for protocol in protocols_response.json()["content"]:
            protocols.append(
                (
                   protocol["id"],
                    "<%s>%s - %s" % (protocol["type"], protocol["id"], protocol["name"]),
                )
            )

    setattr(
        StaticForm,
        "protocol_id",
        SelectField(
            "Protocol/Collection", choices=protocols,
        ),
    )

    return StaticForm()