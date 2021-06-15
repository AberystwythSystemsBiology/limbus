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
from datetime import datetime
from ...enums import Colour, DisposalInstruction
from wtforms import (
    BooleanField,
    StringField,
    TextAreaField,
    SubmitField,
    DateField,
    TimeField,
)

from wtforms.validators import DataRequired, Optional


def PatientConsentQuestionnaire(consent_template: dict) -> FlaskForm:
    class StaticForm(FlaskForm):
        consent_id = StringField(
            "Patient Consent Form ID/Code",
            description="The identifying code of the signed patient consent form.",
        )

        comments = TextAreaField("Comments")
        time = TimeField("Time of Consent", default=datetime.now())
        undertaken_by = StringField(
            "Undertaken By",
            description="The initials of the individual who undertook the consent event.",
        )
        date = DateField("Date of Consent", default=datetime.today())
        time = TimeField("Time of Consent", default=datetime.now())

        submit = SubmitField("Continue")

    for question in consent_template["questions"]:
        setattr(
            StaticForm,
            str(question["id"]),
            BooleanField(
                question["question"], render_kw={"question_type": question["type"]}
            ),
        )

    return StaticForm()
