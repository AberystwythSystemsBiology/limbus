from flask_wtf import FlaskForm

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, ValidationError, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, URL

class BiobankRegistrationForm(FlaskForm):
    name = StringField("Biobank Name", validators=[DataRequired()], description="Textual string of letters denoting the name of the biobank in English")
    url = StringField("Biobank Website", validators=[URL()], description="Textual string of letters with the complete http-address for the biobank")
    description = StringField(description="Textual string of letters with a description about the biobank in English.")
    country = SelectField("Country", choices=[("gb", "United Kingdom")])

    submit = SubmitField("Register")
