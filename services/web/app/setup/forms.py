from flask_wtf import FlaskForm
from wtforms import (
    PasswordField,
    StringField,
    SubmitField,
    ValidationError,
    SelectField,
)
from wtforms.validators import DataRequired, Email, EqualTo, URL, ValidationError , Optional
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

    submit = SubmitField("Register")
