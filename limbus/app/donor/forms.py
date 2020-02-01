from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import SelectField, StringField, SubmitField

from .enums import DonorSex, DonorRace

class DonorCreationForm(FlaskForm):
    age = StringField("Age", validators=[DataRequired()], description="Age in Years")
    race = SelectField("Race", validators=[DataRequired()], choices=DonorRace.choices())

    height = StringField("Height (cm)", validators=[DataRequired()])
    weight = StringField("Weight (kg)", validators=[DataRequired()])

    sex = SelectField("Biological Sex", choices=DonorSex.choices(), validators=[DataRequired()])

    submit = SubmitField()