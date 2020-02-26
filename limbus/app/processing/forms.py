from flask_wtf import FlaskForm
from wtforms import FileField, StringField, SubmitField, ValidationError, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, URL

from ..sample.enums import SampleType

class NewProtocolForm(FlaskForm):
    name = StringField("Protocol Name", validators=[DataRequired()])
    type = SelectField("Sample Type", validators=[DataRequired()], choices=[(x.name, x.value) for x in SampleType])
    submit = SubmitField("Submit")


class FluidCheckList(FlaskForm):
    pc = BooleanField("Pre-Centrifuge?")
    ce = BooleanField("Centrifuge?")
    sc = BooleanField("Second Centrifuge?")
    pd = BooleanField("Post-Centrifuge Delay?")
    submit = SubmitField("Submit")