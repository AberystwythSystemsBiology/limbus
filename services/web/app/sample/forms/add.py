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
    SelectField,
    StringField,
    TextAreaField,
    SubmitField,
    FloatField,
    DateField,
    BooleanField,
    TimeField,
    IntegerField,
)
from wtforms.validators import DataRequired, Length, ValidationError, Optional
from wtforms.widgets import TextInput

from datetime import datetime

from ..enums import *
import requests
from ...misc import get_internal_api_header


def SampleAliquotingForm(processing_templates: dict) -> FlaskForm:
    class StaticForm(FlaskForm):
        aliquot_date = DateField(
            "Aliquot Date", validators=[DataRequired()], default=datetime.today()
        )
        aliquot_time = TimeField(
            "Aliquot Time", validators=[DataRequired()], default=datetime.now()
        )
        comments = TextAreaField("Comments")
        container_base_type = SelectField(
            "Container base type", choices=ContainerBaseType.choices()
        )

        processed_by = StringField(
            "Processed By",
            description="The initials of the individual who collected the sample.",
        )
        submit = SubmitField("Submit")

    processing_template_choices = []

    for protocol in processing_templates:
        processing_template_choices.append(
            [protocol["id"], "LIMBPRO-%i: %s" % (protocol["id"], protocol["name"])]
        )

    setattr(
        StaticForm,
        "processing_protocol",
        SelectField(
            "Processing Protocol", choices=processing_template_choices, coerce=int
        ),
    )

    setattr(
        StaticForm,
        "processed_by",
        # SelectField("Processed By", choices=user_choices, coerce=int),
        # sample processor not necessarily in the system
        StringField("Processed By"),
    )

    return StaticForm()


def CustomAttributeSelectForm(custom_attributes: dict) -> FlaskForm:
    class StaticForm(FlaskForm):
        submit = SubmitField("Submit")

    for attribute in custom_attributes:
        setattr(
            StaticForm,
            str(attribute["id"]),
            BooleanField(attribute["term"], render_kw={"attribute": attribute}),
        )

    return StaticForm()
