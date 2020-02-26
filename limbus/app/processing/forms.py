from flask_wtf import FlaskForm
from wtforms import FileField, StringField, SubmitField, ValidationError, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, URL

from ..sample.enums import SampleType

from .enums import FluidContainer, ProcessingTemps, ProcessingTimes

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

def ProcessingInformation(type, steps):
    class StaticForm(FlaskForm):
        pass


    def _pre_centrifuge():
        setattr(StaticForm, "pre_centr_temp", SelectField("Pre-Centrifuge Temp", validators=[DataRequired()],
        choices=[(x.name, x.value) for x in ProcessingTemps]))

        setattr(StaticForm, "pre_centr_time", SelectField("Pre-Centrifuge Time", validators=[DataRequired()],
        choices=[(x.name, x.value) for x in ProcessingTimes]))

    def _centrifuge():
        pass

    def _second_centrifuge():
        pass

    def _post_centrifuge():
        pass
    
    if type == "FLU":
        setattr(StaticForm,"container", SelectField("Fluid Container", validators=[DataRequired()],
                       choices=[(x.name, x.value) for x in FluidContainer]))

        if steps["pre-cent"]:
            _pre_centrifuge()

    setattr(StaticForm, "submit", SubmitField())
    return StaticForm()