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
    FileField,
    StringField,
    SubmitField,
    ValidationError,
    SelectField,
    TextAreaField,
    BooleanField,
)
from wtforms.validators import DataRequired, Email, EqualTo, URL
import os

from .models import DocumentType

# Custom Validators


def validate_pdf(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    if not ext.lower() == ".pdf":
        raise ValidationError("Unsupported file extension.")


def check_document_name(id):
    def _check_document_name(form, field):
        if field.data != "LIMBDOC-%s" % (str(id)):
            raise ValidationError("Incorrect entry")

    return _check_document_name

def check_file_name(name):
    def _check_file_name(form, field):
        if field.data != name:
            raise ValidationError("%s is not the name of the file. Please try again." % (field.data))
    return _check_file_name


def DocumentFileDeletionForm(name):
    class StaticForm(FlaskForm):
        submit = SubmitField()

    setattr(
        StaticForm,
        "name",
        StringField(
            "Please enter %s to continue" % (name),
            [DataRequired(), check_file_name(name=name)]
        )
    )

    return StaticForm()

def DocumentLockForm(id):
    class StaticForm(FlaskForm):
        submit = SubmitField("Submit")

    setattr(
        StaticForm,
        "name",
        StringField(
            "Please enter LIMBDOC-%s to continue" % (str(id)),
            [DataRequired(), check_document_name(id=id)],
        ),
    )

    return StaticForm()


class DocumentCreationForm(FlaskForm):
    name = StringField(
        "Document Name",
        validators=[DataRequired()],
        description="Textual string of letters denoting the name of the document in English",
    )
    description = TextAreaField("Document Description")

    type = SelectField(
        "Document Type",
        validators=[DataRequired()],
        choices=[(x.name, x.value) for x in DocumentType],
    )

    file = FileField("File Upload", validators=[DataRequired()])

    submit = SubmitField("Submit")


class PatientConsentFormInformationForm(FlaskForm):
    academic = BooleanField("Academic Studies")
    commercial = BooleanField("Commercial Studies")
    animal = BooleanField("Animal Studies")
    genetic = BooleanField("Genetic Studies")

    submit = SubmitField("Continue")


class UploadFileForm(FlaskForm):
    file = FileField("Document File", validators=[DataRequired()])
    submit = SubmitField("Upload")
