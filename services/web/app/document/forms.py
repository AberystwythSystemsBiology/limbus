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
)
from wtforms.validators import DataRequired, Email, EqualTo, URL

from .models import DocumentType


class DocumentUploadForm(FlaskForm):
    name = StringField(
        "Document Name",
        validators=[DataRequired()],
        description="Textual string of letters denoting the name of the document in English",
    )
    type = SelectField(
        "Document Type",
        validators=[DataRequired()],
        choices=[(x.name, x.value) for x in DocumentType],
    )
    description = StringField("Document Description")

    submit = SubmitField("Continue")


class PatientConsentFormInformationForm(FlaskForm):
    academic = BooleanField("Academic Studies")
    commercial = BooleanField("Commercial Studies")
    animal = BooleanField("Animal Studies")
    genetic = BooleanField("Genetic Studies")

    submit = SubmitField("Continue")


class DocumentUploadFileForm(FlaskForm):
    file = FileField(validators=[DataRequired()])
    submit = SubmitField("Upload")
