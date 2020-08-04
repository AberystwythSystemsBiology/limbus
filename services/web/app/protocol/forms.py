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



from wtforms.validators import DataRequired, EqualTo, URL, Optional

from .enums import ProtocolType

class ProtocolCreationForm(FlaskForm):
    name = StringField(
        "Protocol Name",
        validators=[DataRequired()],
        description="Textual string of letters denoting the name of the protocol in English",
    )
    type = SelectField(
        "Protocol Type",
        validators=[DataRequired()],
        choices=[(x.name, x.value) for x in ProtocolType],
    )

    doi = StringField(
        "Digital Object Identifier (DOI)",
        validators=[URL(), Optional()],
        description="The persistent identifier or handle used to identify objects uniquely."
    )

    description = StringField("Document Description")

    submit = SubmitField("Submit")
