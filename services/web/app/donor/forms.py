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

from flask_wtf import FlaskForm
from wtforms import (
    FileField,
    StringField,
    SubmitField,
    ValidationError,
    SelectField,
    BooleanField,
    DecimalField,
    DateField,
    IntegerField,
    HiddenField,
)

# from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Email, EqualTo, URL, Optional
from .enums import RaceTypes, BiologicalSexTypes, DonorStatusTypes
from ..sample.enums import Colour

class DonorFilterForm(FlaskForm):

    sex = SelectField(
        "Biological Sex",
        choices=BiologicalSexTypes.choices(with_none=True),
    )
    status = SelectField("Status", choices=DonorStatusTypes.choices(with_none=True))
    race = SelectField(
        "Race",
        choices=RaceTypes.choices(with_none=True),
    )


def DonorCreationForm(sites: dict):
    class StaticForm(FlaskForm):
        colour = SelectField("Colour", choices=Colour.choices())

        age = StringField(
            "Age", description="The length of time that a donor has lived for in years."
        )
        sex = SelectField(
            "Biological Sex",
            choices=BiologicalSexTypes.choices(),
        )

        mpn = StringField("Master Patient Number")

        registration_date = DateField("Registration Date")

        status = SelectField("Status", choices=DonorStatusTypes.choices())

        death_date = DateField("Date of Death")

        weight = StringField("Weight (kg)", validators=[DataRequired()])
        height = StringField("Height (cm)", validators=[DataRequired()])

        race = SelectField(
            "Race",
            choices=RaceTypes.choices(),
        )

        submit = SubmitField("Submit")

    site_choices = []
    for site in sites:
        site_choices.append([site["id"], "LIMBSIT-%i: %s" % (site["id"], site["name"])])

    setattr(StaticForm, "site",         # enrollment site
        SelectField(
            "Enrollment Site",
            choices=site_choices,
            coerce=int
        ))

    return StaticForm()

