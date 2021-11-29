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
    PasswordField,
    StringField,
    SubmitField,
    ValidationError,
    SelectField,
    BooleanField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    URL,
    ValidationError,
    Optional,
)
from ukpostcodeutils import validation

import pycountry


def post_code_validator(form, field):
    if not validation.is_valid_postcode(field.data):
        raise ValidationError("Invalid UK Post Code")


class SiteRegistrationForm(FlaskForm):
    name = StringField(
        "Site Name",
        validators=[DataRequired()],
        description="Textual string of letters denoting the name of the site in English",
    )
    url = StringField(
        "Site Website",
        validators=[URL(), Optional()],
        description="Textual string of letters with the complete http-address for the site",
    )
    description = StringField(
        "Site Description",
        description="Textual string of letters with a description about the site in English.",
    )

    address_line_one = StringField("Address Line1", validators=[DataRequired()])
    address_line_two = StringField("Address Line2")
    city = StringField("Town/City", validators=[DataRequired()])
    county = StringField("County", validators=[DataRequired()])
    country = SelectField(
        "Country",
        validators=[DataRequired()],
        default = "GB",
        choices=sorted(
            [(country.alpha_2, country.name) for country in pycountry.countries],
            key=lambda x: x[1],
        ),
    )
    post_code = StringField(
        "Post Code",
        description="Please enter the Post Code without spaces.",
        validators=[DataRequired(), post_code_validator],
    )

    is_external = BooleanField("Is External", render_kw={"checked": ""})

    submit = SubmitField("Register")
