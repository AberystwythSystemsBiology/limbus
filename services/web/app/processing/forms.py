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
    RadioField,
)
from wtforms.validators import DataRequired, Email, EqualTo, URL

from .enums import ProtocolSampleType, ProtocolTypes


class NewProtocolForm(FlaskForm):
    name = StringField("Protocol Name", validators=[DataRequired()])

    protocol_type = SelectField("Protocol Type", choices=ProtocolTypes.choices())

    sample_type = SelectField("Sample Type", choices=ProtocolSampleType.choices())

    document_upload = FileField()

    submit = SubmitField("Submit")


class FluidCheckList(FlaskForm):
    pc = BooleanField("Pre-Centrifuge?")
    ce = BooleanField("Centrifuge?")
    sc = BooleanField("Second Centrifuge?")
    pd = BooleanField("Post-Centrifuge Delay?")
    submit = SubmitField("Submit")
