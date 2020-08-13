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

from flask import url_for
import requests

from flask_wtf import FlaskForm
from wtforms import (
    FileField,
    StringField,
    SubmitField,
    ValidationError,
    SelectField,
    TextAreaField,
    BooleanField,
    RadioField,
)


from wtforms.validators import DataRequired, EqualTo, URL, Optional, Length
from flask_mde import Mde, MdeField

from .enums import ProtocolType, ProtocolTextType
from ..misc import get_internal_api_header


class ProtocolCreationForm(FlaskForm):
    name = StringField(
        "Protocol Name",
        validators=[DataRequired()],
        description="Textual string of letters denoting the name of the protocol in English",
    )

    description = TextAreaField(
        "Description", description="A brief description of the Protocol."
    )

    type = SelectField(
        "Protocol Type",
        validators=[DataRequired()],
        choices=[(x.name, x.value) for x in ProtocolType],
    )

    doi = StringField(
        "Digital Object Identifier (DOI)",
        validators=[URL(), Optional()],
        description="The persistent identifier or handle used to identify objects uniquely.",
    )

    description = StringField("Document Description")

    submit = SubmitField("Submit")


class MdeForm(FlaskForm):
    type = SelectField(
        "Protocol Text Type", choices=[(x.name, x.value) for x in ProtocolTextType],
    )
    editor = MdeField()

    submit = SubmitField("Submit")


def DocumentAssociationForm() -> FlaskForm:
    class StaticForm(FlaskForm):
        description = TextAreaField("Description")
        submit = SubmitField("Submit")

    response = requests.get(
        url_for("api.document_home", _external=True), headers=get_internal_api_header()
    )

    documents = []

    if response.status_code == 200:
        for doc in response.json()["content"]:
            documents.append([doc["id"], "LIMBDOC-%i: %s" % (doc["id"], doc["name"])])

    setattr(
        StaticForm, "document", SelectField("Document", choices=documents, coerce=int),
    )

    return StaticForm()
