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

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    TextAreaField,
    SelectField,
    DateField,
    DecimalField
)

from wtforms.validators import DataRequired

from datetime import datetime
from ..enums import (
    FixedColdStorageService,
    FixedColdStorageStatus,
    FixedColdStorageTemps,
    ColdStorageServiceResult,
    FixedColdStorageType
)


class ColdStorageServiceReportForm(FlaskForm):
    date = DateField(
        "Service Date",
        validators=[DataRequired()],
        default=datetime.today()
    )

    conducted_by = StringField(
        "Conducted By"
    )

    temp = DecimalField(
        "Temperature",
        default=0.0
    )

    status = SelectField(
        "Storage Status",
        choices=ColdStorageServiceResult.choices()

    )

    comments = TextAreaField(
        "Comments"
    )

    submit = SubmitField("Submit")
    # Date
    # Conducted by
    # Temp
    # Status
    # Comments
    # Submit

class ColdStorageForm(FlaskForm):

    alias = StringField(
        "Alias",
        validators=[DataRequired()]
    )

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

    status = SelectField(
        "Status",
        choices=FixedColdStorageStatus.choices(),
        validators=[DataRequired()]
    )

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
