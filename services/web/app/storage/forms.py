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

from flask import url_for
from datetime import datetime
import pycountry
from flask_wtf import FlaskForm
import requests
from wtforms import (
    PasswordField,
    StringField,
    BooleanField,
    RadioField,
    SubmitField,
    DateField,
    TimeField,
    TextAreaField,
    FileField,
    ValidationError,
    SelectField,
    IntegerField,
)
from wtforms.validators import DataRequired, Email, EqualTo, URL, ValidationError
from ..setup.forms import post_code_validator
from ..misc import get_internal_api_header
from .enums import *
from ..sample.forms import Colour


class RoomRegistrationForm(FlaskForm):
    name = StringField("Room Name", validators=[DataRequired()])
    submit = SubmitField("Register Room")


class BuildingRegistrationForm(FlaskForm):
    name = StringField("Building Name", validators=[DataRequired()])
    submit = SubmitField("Register Building")


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


class NewSampleRackForm(FlaskForm):
    serial = StringField("Serial Number", validators=[DataRequired()])
    num_rows = IntegerField("Number of Rows", validators=[DataRequired()], default=1)
    num_cols = IntegerField("Number of Columns", validators=[DataRequired()], default=1)
    description = TextAreaField("Description")
    colours = SelectField("Colour", choices=Colour.choices())
    submit = SubmitField("Register")


class NewCryovialBoxFileUploadForm(FlaskForm):
    serial = StringField("Serial Number", validators=[DataRequired()])
    description = TextAreaField("Description")
    colour = SelectField("Colour", choices=Colour.choices())
    barcode_type = SelectField(
        "Barcode Type",
        choices=[("uuid", "LImBuS UUID"), ("biobank_barcode", "Biobank Barcode")],
        description="The barcode attribute to cross reference against."
        )
    file = FileField("File", validators=[DataRequired()])
    submit = SubmitField("Upload File")


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


class ColdStorageForm(FlaskForm):
    serial_number = StringField(
        "Serial Number",
        description="Equipment serial number is a serial number that identifies an equipment used in the measuring by its serial number.",
    )

    manufacturer = StringField(
        "Manufacturer",
        validators=[DataRequired()],
        description="The storage facility manufacturer.",
    )

    comments = TextAreaField("Comments")

    temperature = SelectField(
        "Temperature",
        choices=FixedColdStorageTemps.choices(),
        validators=[DataRequired()],
        description="The temperature of the inside of the storage facility.",
    )

    type = SelectField(
        "Storage Type",
        choices=FixedColdStorageType.choices(),
        validators=[DataRequired()],
        description="A facility that provides storage for any type of biospecimen and/or biospecimen container.",
    )

    submit = SubmitField("Register")


def SampleToEntityForm(samples: list) -> FlaskForm:

    samples_choices = []
    for sample in samples:
        samples_choices.append([int(sample["id"]), sample["uuid"]])

    class StaticForm(FlaskForm):
        date = DateField("Entry Date", validators=[DataRequired()], default=datetime.today())
        time = TimeField("Entry Time", validators=[DataRequired()], default=datetime.now())
        entered_by = StringField(
            "Entered By",
            description="The initials of the person that entered the sample.",
        )
        submit = SubmitField("Submit")

    setattr(
        StaticForm,
        "samples",
        SelectField(
            "Sample", choices=samples_choices, validators=[DataRequired()], coerce=int
        ),
    )

    return StaticForm()


def RackToShelfForm(racks: list) -> FlaskForm:
    class StaticForm(FlaskForm):
        date = DateField("Entry Date", validators=[DataRequired()], default=datetime.today())
        time = TimeField("Entry Time", validators=[DataRequired()], default=datetime.now())
        entered_by = StringField(
            "Entered By",
            description="The initials of the person that entered the sample.",
        )
        submit = SubmitField("Submit")

    choices = []

    for rack in racks:
        choices.append(
            [
                rack["id"],
                "LIMBRACK-%s: %s (%i x %i)"
                % (rack["id"], rack["uuid"], rack["num_rows"], rack["num_cols"]),
            ]
        )

    setattr(
        StaticForm, "racks", SelectField("Sample Rack", choices=choices, coerce=int)
    )

    return StaticForm()


def CryoBoxFileUploadSelectForm(sample_data: dict):
    class StaticForm(FlaskForm):
        submit = SubmitField("Submit Cryovial Box")

    for position, info in sample_data.items():
        setattr(
            StaticForm,
            position,
            BooleanField(
                position,
                render_kw={
                    "_selectform": True,
                    "_sample": info,
                },
            ),
        )

    return StaticForm()
