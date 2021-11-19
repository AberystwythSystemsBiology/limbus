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


from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Optional
from wtforms import (
    SelectField,
    SubmitField,
    DateField,
    TimeField,
    TextAreaField,
    StringField,
)
from ..enums import DisposalReason
from datetime import datetime


def SampleDisposalInstructionForm(protocols: list) -> FlaskForm:
    class StaticForm(FlaskForm):
        disposal_date = DateField(
            "Sample Disposal Date (*)",
            description="The date in which the sample is required to be disposed of.",
            default=datetime.today,
            validators=[Optional()],
        )

        disposal_instruction = SelectField(
            "Sample Disposal Instruction",
            choices=DisposalInstruction.choices(),
            description="The method of sample disposal.",
            validators=[Optional()],
        )

        disposal_comments = TextAreaField("Sample Disposal Comments")
        # approved_by = TextAreaField("To be approved by ")
        submit = SubmitField("Submit")

    return StaticForm()


def SampleDisposalEventForm(protocols: list) -> FlaskForm:
    class StaticForm(FlaskForm):
        protocol_id = SelectField("Protocol", choices=protocols, coerce=int)

        reason = SelectField(
            "Disposal Reason",
            description="Reason for disposal",
            choices=DisposalReason.choices(),
        )

        comments = TextAreaField("Comments")

        date = DateField(
            "Disposal Event Date",
            validators=[DataRequired()],
            description="The date in which the disposal was undertaken.",
            default=datetime.today(),
        )

        time = TimeField(
            "Disposal Event Time",
            default=datetime.now(),
            validators=[DataRequired()],
            description="The time at which the disposal was undertaken.",
        )

        undertaken_by = StringField(
            "Undertaken By",
            description="The initials of the individual who undertook the disposal event.",
        )

        submit = SubmitField("Submit")

    return StaticForm()
