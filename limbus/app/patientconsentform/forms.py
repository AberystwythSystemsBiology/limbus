from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, DateField, BooleanField
from wtforms.validators import DataRequired


class NewConsentFormTemplate(FlaskForm):
    name = StringField(
        "Template Name",
        validators=[DataRequired()],
        description="Descriptive name for the Consent Form Template",
    )



    version = StringField("Template Version", description="Version of the Protocol (if required)")



    submit = SubmitField("Submit")
