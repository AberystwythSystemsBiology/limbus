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
from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SelectField,
    SelectMultipleField,
    SubmitField,
    DateField,
    TimeField,
)
import requests
from ...misc import get_internal_api_header

import pycountry

from wtforms.validators import DataRequired, Email, EqualTo, URL, ValidationError
from ...setup.forms import post_code_validator


class SiteRegistrationForm(FlaskForm):
    name = StringField("Site Name", validators=[DataRequired()])
    address_line_one = StringField("Address Line1", validators=[DataRequired()])
    address_line_two = StringField("Address Line2")
    city = StringField("Town/City", validators=[DataRequired()])
    county = StringField("County", validators=[DataRequired()])
    country = SelectField(
        "Country",
        validators=[DataRequired()],
        choices=[(country.alpha_2, country.name) for country in pycountry.countries],
    )
    post_code = StringField(
        "Post Code", validators=[DataRequired(), post_code_validator]
    )

    submit = SubmitField("Register Site")


def SampleToEntityForm(samples: list) -> FlaskForm:

    samples_choices = [[0, '--- Select a sample ---']]
    for sample in samples:
        sample_check_response = requests.get(url_for("api.storage_sample_to_entity_check",id=int(sample["id"]), _external=True),headers=get_internal_api_header())
        if not sample_check_response.json()["content"] == "SCT":
            samples_choices.append([int(sample["id"]), sample["uuid"]])

    class StaticForm(FlaskForm):
        date = DateField(
            "Entry Date", validators=[DataRequired()], default=datetime.today()
        )
        time = TimeField(
            "Entry Time", validators=[DataRequired()], default=datetime.now()
        )
        entered_by = StringField(
            "Entered By",
            description="The initials of the person that entered the sample.",
        )
        submit = SubmitField("Submit")

    setattr(
        StaticForm,
        "samples",
        SelectField(
            "Sample", choices=samples_choices, validators=[DataRequired()], coerce=int,render_kw={'onchange': "check_sample()"}
        ),
    )

    return StaticForm()

def SamplesToEntityForm(samples: list) -> FlaskForm:

    samples_choices = [[0, '--- Select at least one samples ---']]
    for sample in samples:
        samples_choices.append([int(sample["id"]), sample["uuid"]])

    print("samples_choices ", samples_choices)

    class StaticForm(FlaskForm):
        date = DateField(
            "Entry Date", validators=[DataRequired()], default=datetime.today()
        )
        time = TimeField(
            "Entry Time", validators=[DataRequired()], default=datetime.now()
        )
        entered_by = StringField(
            "Entered By",
            description="The initials of the person that entered the sample.",
        )
        submit = SubmitField("Submit")

    default_choices = [int(s[0]) for s in samples_choices if int(s[0]) >0]

    setattr(
        StaticForm,
        "samples",
        SelectMultipleField(
            "Sample(s)", choices=samples_choices, default=default_choices, validators=[DataRequired()], coerce=int, #render_kw={'onchange': "check_sample()"}
        ),
    )

    return StaticForm()


from .building import *
from .lts import *
from .rack import *
from .room import *
from .shelf import *
