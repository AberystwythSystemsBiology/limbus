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
    # DateField,
    IntegerField,
    HiddenField,
)

# from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Email, EqualTo, URL


from .enums import RaceTypes, BiologicalSexTypes, DonorStatusTypes


class DonorCreationForm(FlaskForm):

    age = StringField(
        "Age (years)", description="The length of time that a donor has lived in years."
    )
    sex = SelectField("Sex", choices=BiologicalSexTypes.choices())
    status = SelectField("Status", choices=DonorStatusTypes.choices())

    death_date = StringField("Date of Death", description="YYYY-mm-dd")

    weight = StringField("Weight (kg)")
    height = StringField("Height (cm)")

    race = SelectField("Race", choices=RaceTypes.choices())

    submit = SubmitField("Submit")
