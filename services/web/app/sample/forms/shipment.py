# Copyright (C) 2021 Keiron O'Shea <keo7@aber.ac.uk>
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

from flask.app import Flask
from flask_wtf import FlaskForm
from wtforms import (
    SelectField,
    StringField,
    BooleanField,
    SubmitField,
    DateField,
    TimeField,
    TextAreaField,
)
from wtforms.validators import DataRequired
from ..enums import SampleShipmentStatusStatus
from datetime import datetime


def SampleShipmentEventForm(sites: list) -> FlaskForm:
    class StaticForm(FlaskForm):
        date = DateField(
            "Shipment Request Date",
            description="The date in which the shipment order was made.",
            default=datetime.today(),
        )

        time = TimeField(
            "Shipment Request Time",
            description="The time in which the shipment order was made.",
            default=datetime.now(),
        )

        undertaken_by = StringField(
            "Undertaken By",
            description="The initials of the individual who undertook the shipment event.",
        )

        comments = TextAreaField("Comments", description="Any relevant observations.")
        submit = SubmitField("Submit")

    setattr(
        StaticForm, "site_id", SelectField("Recieving Site", choices=sites, coerce=int)
    )

    return StaticForm()


def SampleShipmentStatusUpdateform(data={}) -> FlaskForm:
    class StaticForm(FlaskForm):
        status = SelectField(
            "Shipment Status",
            validators=[DataRequired()],
            choices=SampleShipmentStatusStatus.choices(),
        )

        tracking_number = TextAreaField("Tracking number")
        comments = TextAreaField("Comments")
        date = DateField(
            "Shipment Status Updated Date",
            default=datetime.today(),
        )

        time = TimeField(
            "Shipment Status Updated Time",
            default=datetime.now(),
        )
        submit = SubmitField("Update Status")

    return StaticForm(data=data)
