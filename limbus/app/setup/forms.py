from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, ValidationError, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, URL
from ..auth.enums import Title

class BiobankRegistrationForm(FlaskForm):
    name = StringField(
        "Biobank Name",
        validators=[DataRequired()],
        description=
        "Textual string of letters denoting the name of the biobank in English"
    )
    url = StringField(
        "Biobank Website",
        validators=[URL()],
        description=
        "Textual string of letters with the complete http-address for the biobank"
    )
    description = StringField(
        description=
        "Textual string of letters with a description about the biobank in English."
    )
    submit = SubmitField("Register Biobank")

from ..auth.forms import RegistrationForm

class AdministratorRegistrationForm(RegistrationForm):
    title = SelectField("Title",
                              validators=[DataRequired()],
                              choices=Title.choices())

    first_name = StringField("First Name", validators=[DataRequired()])
    middle_name = StringField("Middle Name")
    last_name = StringField("Last Name", validators=[DataRequired()])
