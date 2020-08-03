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
from wtforms import SelectField, StringField, SubmitField, DateField, BooleanField, TextAreaField
from wtforms.validators import DataRequired
from .enums import QuestionType

class NewConsentFormTemplateForm(FlaskForm):
    name = StringField(
        "Consent Form Title",
        validators=[DataRequired()],
        description="Descriptive name/title for the Consent Form Template",
    )

    description = TextAreaField(
        "Description"
    )

    version = StringField(
        "Template Version", description="Version of the Protocol"
    )

    submit = SubmitField("Submit")

class NewConsentFormQuestionForm(FlaskForm):
    question = TextAreaField("Question", validators=[DataRequired()])
    # TODO: Fill this out!!
    type = SelectField("Question Type", description="Something here detailing what each of these does and why.", choices=QuestionType.choices())
    submit = SubmitField("Submit")