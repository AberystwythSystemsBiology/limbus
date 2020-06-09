
from flask_wtf import FlaskForm
from wtforms import (
    FileField,
    StringField,
    SubmitField,
    ValidationError,
    SelectField,
    BooleanField,
    DecimalField,
    DateField,
    IntegerField
)
from wtforms.validators import DataRequired, Email, EqualTo, URL


from .enums import RaceTypes, BiologicalSexTypes, DonorStatusTypes

class DonorCreationForm(FlaskForm):

    age = IntegerField("Age (years)", description="The length of time that a donor has lived in years.")
    sex = SelectField("Sex", choices=BiologicalSexTypes.choices())
    status = SelectField("Status", choices=DonorStatusTypes.choices())
    death_date = DateField("Date of Death")
    weight = DecimalField("Weight (kg)")
    height = DecimalField("Height (cm)")

    race = SelectField("Race", choices=RaceTypes.choices())

    submit = SubmitField("Submit")