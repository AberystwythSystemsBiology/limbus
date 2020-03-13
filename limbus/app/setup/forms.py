from flask_wtf import FlaskForm
from wtforms import (
    PasswordField,
    StringField,
    SubmitField,
    ValidationError,
    SelectField,
)
from wtforms.validators import DataRequired, Email, EqualTo, URL, ValidationError
from ukpostcodeutils import validation
from ..auth.enums import Title
import pycountry


def post_code_validator(form, field):
    if not validation.is_valid_postcode(field.data):
        raise ValidationError("Invalid UK Post Code")


class BiobankRegistrationForm(FlaskForm):
    name = StringField(
        "Biobank Name",
        validators=[DataRequired()],
        description="Textual string of letters denoting the name of the biobank in English",
    )
    url = StringField(
        "Biobank Website",
        validators=[URL()],
        description="Textual string of letters with the complete http-address for the biobank",
    )
    description = StringField(
        "Biobank Description",
        description="Textual string of letters with a description about the biobank in English.",
    )

    address_line_one = StringField("Address Line1", validators=[DataRequired()])
    address_line_two = StringField("Address Line2")
    city = StringField("Town/City", validators=[DataRequired()])
    county = StringField("County", validators=[DataRequired()])
    country = SelectField(
        "Country",
        validators=[DataRequired()],
        choices=[(country.alpha_2, country.name) for country in pycountry.countries],
    )
    post_code = StringField(
        "Post Code", description="Please enter the Post Code without spaces.", validators=[DataRequired(), post_code_validator],
    )

    submit = SubmitField("Register Biobank")


from ..auth.forms import RegistrationForm


class AdministratorRegistrationForm(RegistrationForm):
    title = SelectField("Title", validators=[DataRequired()], choices=Title.choices())

    first_name = StringField("First Name", validators=[DataRequired()])
    middle_name = StringField("Middle Name")
    last_name = StringField("Last Name", validators=[DataRequired()])
