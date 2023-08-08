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


def SampleShipmentEventForm(
    protocols=[], sites=[], sites_ext=[], addresses=[], data={}
) -> FlaskForm:
    class StaticForm(FlaskForm):
        protocol_id = SelectField(
            "Sample Transfer Protocol", choices=protocols, coerce=int
        )

        site_id = SelectField("Destination (internal)", choices=sites, coerce=int)
        external_site_id = SelectField(
            "Destination (external)", choices=sites_ext, coerce=int
        )

        address_id = SelectField("Shipping Address", choices=addresses, coerce=int)

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
            validators=[DataRequired()],
        )

        comments = TextAreaField("Comments", description="Any relevant observations.")
        submit = SubmitField("Submit")

        def validate(self):
            # print("form", str(self.data))
            if not FlaskForm.validate(self):
                return False

            success = True
            if self.site_id.data == 0 and self.external_site_id.data == 0:
                self.site_id.errors.append("Site required.")
                self.external_site_id.errors.append("Site required.")
                success = False
            if self.address_id.data == 0 and self.external_site_id.data == 0:
                self.address_id.errors.append("Address required.")
                success = False

            return success

    return StaticForm(data=data)


def SampleShipmentStatusUpdateform(data={}) -> FlaskForm:
    class StaticForm(FlaskForm):
        status = SelectField(
            "Shipment Status",
            validators=[DataRequired()],
            choices=SampleShipmentStatusStatus.choices(),
        )

        courier = StringField("Courier")
        # courier = SelectField(
        #     "Courier",
        #     validators=[Optional()],
        #     default="",
        #     choices=courier_choices,
        # )

        tracking_number = StringField("Tracking number")
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
