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
    FormField,
)

from wtforms.validators import DataRequired, Optional

# def PatientConsentQuestionnaire(consent_template: dict) -> FlaskForm:
#     class StaticForm(FlaskForm):
#
#         template_name = TextAreaField("template_name")
#         template_version = StringField("version")
#
#         identifier = StringField(
#             "Donor Consent Form ID/Code",
#             description="The identifying code of the signed donor consent form.",
#         )
#
#         comments = TextAreaField("Comments")
#
#         date = DateField("Date of Consent", default=datetime.today())
#         undertaken_by = StringField(
#             "Communicated by",
#         )
#
#         study_select = SelectField(
#             "Study/Trial",
#             validators=[Optional()],
#             choices=study_protocols,
#             description="Protocol of the study/trial recruiting the donor originally.",
#             coerce=int,
#         )
#
#         study = FormField(DonorStudyRegistrationForm)
#
#         submit = SubmitField("Continue")
#
#         def validate(self):
#             if self.study.date.data is None:
#                 self.study.date.data = self.date.data
#
#             if not FlaskForm.validate(self):
#                 return False
#
#             return True
#
#     for question in data["questions"]:
#         checked = ""
#         if checked in question:
#             checked = question["checked"]
#
#         setattr(
#             StaticForm,
#             str(question["id"]),
#             BooleanField(
#                 question["question"],
#                 render_kw={"question_type": question["type"], "checked": checked},
#             ),
#
#         )
#
#     return StaticForm(data=data)
#
# class DonorStudyRegistrationForm(FlaskForm):
#     class Meta:
#         csrf = False
#
#     reference_id = StringField(
#         "Reference Number",
#         description="The reference number for the donor within the study/trial.",
#     )
#     date = DateField(
#         "Date of donor registration/consent",
#         validators = [DataRequired()],
#         default=datetime.today(),
#     )
#
#     comments = TextAreaField(
#         "Comments for donor within the study",
#     )
#
#     undertaken_by = StringField(
#         "Registration Undertaken By",
#     )
