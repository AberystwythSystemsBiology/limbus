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

from flask import url_for
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    IntegerField,
    SubmitField,
    TextAreaField,
    DateField,
    TimeField,
    SelectField,
    SelectMultipleField,
)

import requests
from ...misc import get_internal_api_header

from wtforms.validators import DataRequired

from datetime import datetime


class NewShelfForm(FlaskForm):
    name = StringField(
        "Shelf Name",
        validators=[DataRequired()],
        description="A descriptive name for the shelf, something like top shelf.",
    )

    description = TextAreaField(
        "Shelf Description", description="A brief description of the shelf."
    )

    submit = SubmitField("Register Shelf")


def RackToShelfForm(racks: list) -> FlaskForm:
    class StaticForm(FlaskForm):
        compartment_row = IntegerField("Compartment (row_id)", default=0)
        compartment_col = IntegerField("Compartment (col_id)", default=0)
        date = DateField(
            "Entry Date", validators=[DataRequired()], default=datetime.today()
        )
        time = TimeField(
            "Entry Time", validators=[DataRequired()], default=datetime.now()
        )
        entered_by = StringField(
            "Entered By",
            description="The initials of the person that entered the sample.",
            validators=[DataRequired()],
        )
        submit = SubmitField("Submit")

    choices = []

    for rack in racks:
        rack_check_response = requests.get(
            url_for(
                "api.storage_rack_to_shelf_check", id=int(rack["id"]), _external=True
            ),
            headers=get_internal_api_header(),
        )
        if not rack_check_response.json()["content"] == "RCT":
            choices.append(
                [
                    rack["id"],
                    "LIMBRACK-%s: %s (%i x %i)"
                    % (rack["id"], rack["uuid"], rack["num_rows"], rack["num_cols"]),
                ]
            )

    setattr(
        StaticForm,
        "racks",
        SelectField(
            "Sample Rack",
            choices=choices,
            coerce=int,
            render_kw={"onchange": "check_rack()"},
        ),
    )

    return StaticForm()


def RacksToShelfForm(racks: list) -> FlaskForm:
    class StaticForm(FlaskForm):
        compartment_row = IntegerField("Compartment (row_id)", default=0)
        compartment_col = IntegerField("Compartment (col_id)", default=0)
        date = DateField(
            "Entry Date", validators=[DataRequired()], default=datetime.today()
        )
        time = TimeField(
            "Entry Time", validators=[DataRequired()], default=datetime.now()
        )
        entered_by = StringField(
            "Entered By",
            description="The initials of the person that entered the sample.",
            validators=[DataRequired()],
        )
        submit = SubmitField("Submit")

    choices = [[0, "--- Select at least one racks ---"]]

    for rack in racks:
        choices.append(
            [
                rack["id"],
                "LIMBRACK-%s: %s (%i x %i)"
                % (rack["id"], rack["uuid"], rack["num_rows"], rack["num_cols"]),
            ]
        )

    default_choices = [int(s[0]) for s in choices if int(s[0]) > 0]
    setattr(
        StaticForm,
        "racks",
        SelectMultipleField(
            "Sample Rack(s)",
            choices=choices,
            default=default_choices,
            coerce=int,
        )
        # render_kw={'onchange': "check_rack()"})
    )

    return StaticForm()
