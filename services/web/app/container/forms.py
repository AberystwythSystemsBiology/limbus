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

from wtforms import (
    StringField,
    IntegerField,
    SelectField,
    SubmitField,
    BooleanField,
    TextAreaField,
)

from wtforms.validators import DataRequired, Length
from ..sample.enums import Colour
from .enums import  ContainerUsedFor


class NewFixationType(FlaskForm):

    name = StringField(
        "Fixation Type Name",
        validators=[DataRequired()],
        description="The Canonical Identifier of the Fixation Type."

    )

    manufacturer = StringField(
        "Fixation Type Manufacturer",
        description="If applicable"
    )

    description = TextAreaField(
        "Fixation Type Description",
        description="An optional description of the Fixation Type.",
    )

    formulation = TextAreaField(
        "Fixation Formulation",
        description="An optional description of the Fixation Type.",
    )

    temperature = IntegerField("Temperature (*C)")

    colour = SelectField("Colour", choices=Colour.choices())

    used_for = SelectField(
        "Fixation Type Usage",
        choices=ContainerUsedFor.choices()
    )

    start_hour = IntegerField(
        "Fixation Time: Start Time (hours)",
        validators=[DataRequired()],
        default=0
    )

    end_hour = IntegerField(
        "Fixation Time: End Type (hours)",
        validators=[DataRequired()],
        default=24
    )

    submit = SubmitField("Submit")


class EditContainerForm(FlaskForm):

    name = StringField(
        "Container Name",
        validators=[DataRequired()],
        description="The Canonical Identifier of the Container."

    )

    manufacturer = StringField(
        "Manufacturer",
        description="The Manufacturer of the Container.",
    )

    description = TextAreaField(
        "Container Description",
        description="An optional description of the Container.",
    )
    temperature = IntegerField("Temperature (°C)", default=0)

    fluid = BooleanField("Suitable for Fluids?")
    cellular = BooleanField("Suitable for Cells?")
    tissue = BooleanField("Suitable for Tissue?")
    sample_rack = BooleanField("Suitable for use in a Sample Rack?")
    submit = SubmitField("Submit")


class NewContainerForm(FlaskForm):

    name = StringField(
        "Container Name",
        validators=[DataRequired()],
        description="The Canonical Identifier of the Container."

    )

    manufacturer = StringField(
        "Manufacturer",
        description="The Manufacturer of the Container.",
    )

    description = TextAreaField(
        "Container Description",
        description="An optional description of the Container.",
    )

    colour = SelectField("Colour", choices=Colour.choices())

    used_for = SelectField("Container Usage", choices=ContainerUsedFor.choices())

    fluid = BooleanField("Suitable for Fluids?")
    cellular = BooleanField("Suitable for Cells?")
    tissue = BooleanField("Suitable for Tissue?")
    temperature = IntegerField("Temperature (°C)", default=0)
    sample_rack = BooleanField("Suitable for use in a Sample Rack?")
    submit = SubmitField("Submit")