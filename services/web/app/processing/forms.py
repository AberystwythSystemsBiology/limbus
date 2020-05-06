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
from wtforms.validators import DataRequired, Email, EqualTo, URL

from .enums import ProtocolSampleType, ProtocolTypes


class NewProtocolForm(FlaskForm):
    name = StringField("Protocol Name", validators=[DataRequired()])

    protocol_type = SelectField("Protocol Type", choices=ProtocolTypes.choices())

    sample_type = SelectField("Sample Type", choices=ProtocolSampleType.choices())

    document_upload = FileField()

    submit = SubmitField("Submit")


class FluidCheckList(FlaskForm):
    pc = BooleanField("Pre-Centrifuge?")
    ce = BooleanField("Centrifuge?")
    sc = BooleanField("Second Centrifuge?")
    pd = BooleanField("Post-Centrifuge Delay?")
    submit = SubmitField("Submit")
