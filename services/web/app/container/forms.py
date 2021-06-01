# Copyright (C) 2021  Keiron O'Shea <keo7@aber.ac.uk>
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
from flask import url_for

from wtforms import (
    StringField,
    FloatField,
    SelectField,
    SubmitField,
    ValidationError,
    DateField,
    BooleanField,
    IntegerField,
    TextAreaField,
)

from wtforms.validators import DataRequired, Length
from ..sample.enums import Colour


class NewContainerForm(FlaskForm):
    manufacturer = StringField(
        "Manufacturer",
        validators=[DataRequired()],
        description="The Manufacturer of the Container.",
    )

    identifier = StringField(
        "Canonical Identifier",
        validators=[DataRequired()],
        description="The Canonical Identifier of the Container."

    )

    description = TextAreaField(
        "Container Description",
        description="An optional description of the Container.",
    )

    colour = SelectField(
        "Colour",
        choices=Colour.choices()
    )

    fluid = BooleanField(
        "Suitable for Fluids?"
    )

    cellular = BooleanField(
        "Suitable for Cells?"
    )

    tissue = BooleanField(
        "Suitable for Tissue?"
    )

    min_temperature = FloatField(
        "Minimum Storage Temperature (*C)",

    )

    max_temperature = FloatField(
        "Maximum Storage Temperature (*C)",

    )

    sample_rack = BooleanField(
        "Suitable for use in a Sample Rack?"
    )
    


    submit = SubmitField("Submit")