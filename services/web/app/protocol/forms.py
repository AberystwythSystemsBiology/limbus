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
import re

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


from wtforms.validators import (
    DataRequired,
    EqualTo,
    URL,
    Optional,
    Length,
    AnyOf,
    Regexp,
)
from flask_mde import Mde, MdeField

from .enums import ProtocolType, ProtocolTextType
from ..misc import get_internal_api_header


def ProtocolCreationForm(data={}) -> FlaskForm:
    patterns = {
        "DOI": "\s*DOI\s*:\s*10.\d{4,9}/[-._;()/:A-Z0-9]+$",
        "ISRCTN": "\s*ISRCTN\s*\d{8}$",
        "NCT": "NCT\s*\d{8}$",
        "EUDRACT": "\s*EudraCT\s*:\s*[12]\d{3}-\d{6}-\d{2}$",
        "REC": "\s*REC\s*:\s*[-._;()/:A-Za-z0-9]+$",
        "REF": "\s*REF\s*:\s*[-._;()/:A-Za-z0-9]+$",
    }
    pats = [patterns[k] for k in patterns]

    class StaticForm(FlaskForm):
        name = StringField(
            "Protocol Name",
            validators=[DataRequired()],
            description="Textual string of letters denoting the name of the protocol in English",
        )

        description = TextAreaField(
            "Protocol Description", description="A brief description of the Protocol."
        )

        type = SelectField(
            "Protocol Type",
            validators=[DataRequired()],
            choices=[(x.name, x.value) for x in ProtocolType],
        )

        doi = StringField(
            "Digital Object Identifier (DOI)",
            validators=[Regexp("|".join(pats), re.IGNORECASE), Optional()],
            description="Format DOI:10.xxxx/xxxxxxx (case insensitive); "
            "for study use DOI number or one of the following format: "
            "ISRCTNxxxxxxxx (8 digit with isrctn.com), "
            "NCTxxxxxxxx (8 digit with clinicaltrials.gov), "
            "EudraCT:YYYY-xxxxxx-xx (with clinicaltrialsregister.eu), "
            "REC:xxxxx (REC number), "
            "REF:xxxxx (Internal reference number).",
        )

        submit = SubmitField("Submit")

        def validate(self):
            if not FlaskForm.validate(self):
                return False
            print("!!! doi  ", self.doi.data)
            if self.doi.data != "" and self.doi.data is not None:
                for k in patterns:
                    matched = re.match(
                        patterns[k], self.doi.data.replace(" ", ""), re.IGNORECASE
                    )
                    print("matched: ", matched)
                    if matched:
                        self.doi.data = matched[0].upper()
                        return True

            return True

    return StaticForm(data=data)


class MdeForm(FlaskForm):
    type = SelectField(
        "Protocol Text Type", choices=[(x.name, x.value) for x in ProtocolTextType]
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
        StaticForm, "document", SelectField("Document", choices=documents, coerce=int)
    )

    return StaticForm()
