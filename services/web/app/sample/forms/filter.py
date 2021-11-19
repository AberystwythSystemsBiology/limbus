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

<<<<<<< HEAD
def SampleFilterForm(sites: list, sampletypes: list, data: {}) -> FlaskForm:
    sampletypes.insert(0, (None, "None"))
    # print("sampletype", sampletypes)
=======

def SampleFilterForm() -> FlaskForm:
>>>>>>> d1e264eb56d9321a53ba2c9bf11dec66d1c81902
    class StaticForm(FlaskForm):
        biohazard_level = SelectField(
            "Biohazard Level", choices=BiohazardLevel.choices(with_none=True)
        )

        uuid = StringField("UUID")
        barcode = StringField("Barcode")
        colour = SelectField("Colour", choices=Colour.choices(with_none=True))
<<<<<<< HEAD
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

=======
        base_type = SelectField(
            "Sample Type", choices=SampleBaseType.choices(with_none=True)
        )
        source = SelectField(
            "Sample Source", choices=SampleSource.choices(with_none=True)
        )
        status = SelectField(
            "Sample Status", choices=SampleStatus.choices(with_none=True)
        )

        submit = SubmitField("Filter")

    sites_response = requests.get(
        url_for("api.site_home", _external=True),
        headers=get_internal_api_header(),
    )

    sites = [(None, "None")]
    if sites_response.status_code == 200:
        for site in sites_response.json()["content"]:
            sites.append(
                (
                    site["id"],
                    "<%s>%s - %s" % (site["id"], site["name"], site["description"]),
                )
            )

>>>>>>> d1e264eb56d9321a53ba2c9bf11dec66d1c81902
    setattr(
        StaticForm,
        "current_site_id",
        SelectField(
<<<<<<< HEAD
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
=======
            "Site",
            choices=sites,
>>>>>>> d1e264eb56d9321a53ba2c9bf11dec66d1c81902
        ),
    )

    # Get protocol template list
    protocols_response = requests.get(
        url_for("api.protocol_query", _external=True),
        headers=get_internal_api_header(),
        json={"is_locked": False},
    )

    protocols = [(None, "None")]
    study_protocols = [(None, "None")]
    if protocols_response.status_code == 200:
        for protocol in protocols_response.json()["content"]:
<<<<<<< HEAD
            if protocol["type"] in ["Study", "Collection", "Temporary Storage"]:
                doino = ""
                if protocol["doi"] != "":
                    doino = protocol["doi"].replace("https://","").replace("http://", "")#.split("/")[-1]
                study_protocols.append(
                    (
                        protocol["id"],
                        "<%s>%s [%s] %s" % (protocol["type"], protocol["id"], doino, protocol["name"]),
                    )
                )
            else:
                protocols.append(
                    (
                       protocol["id"],
                        "<%s>%s - %s" % (protocol["type"], protocol["id"], protocol["name"]),
                    )
=======
            protocols.append(
                (
                    protocol["id"],
                    "<%s>%s - %s"
                    % (protocol["type"], protocol["id"], protocol["name"]),
>>>>>>> d1e264eb56d9321a53ba2c9bf11dec66d1c81902
                )

    setattr(
        StaticForm,
        "protocol_id",
        SelectField(
<<<<<<< HEAD
            "Protocol", choices=protocols,
        ),
    )

    setattr(
        StaticForm,
        "source_study",
        SelectField(
            "Source Study", choices=study_protocols,
        ),
    )
    return StaticForm()
=======
            "Protocol/Collection",
            choices=protocols,
        ),
    )

    return StaticForm()
>>>>>>> d1e264eb56d9321a53ba2c9bf11dec66d1c81902
