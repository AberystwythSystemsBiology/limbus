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

from ..sample.enums import SampleType

from .enums import (
    FluidContainer,
    ProcessingTemps,
    ProcessingTimes,
    CentrifugationTime,
    CentrifugationWeights,
    ProtocolTypes,
)


class NewProtocolForm(FlaskForm):
    name = StringField("Protocol Name", validators=[DataRequired()])
    type = SelectField(
        "Sample Type",
        validators=[DataRequired()],
        choices=[(x.name, x.value) for x in SampleType],
    )

    protocol_type = RadioField(
        "Protocol Type",
        choices=[(x.name, x.value) for x in ProtocolTypes],
        validators=[DataRequired()],
    )

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
        setattr(
            StaticForm,
            "pre_centr_temp",
            SelectField(
                "Pre-Centrifuge Temp",
                validators=[DataRequired()],
                choices=[(x.name, x.value) for x in ProcessingTemps],
            ),
        )

        setattr(
            StaticForm,
            "pre_centr_time",
            SelectField(
                "Pre-Centrifuge Time",
                validators=[DataRequired()],
                choices=[(x.name, x.value) for x in ProcessingTimes],
            ),
        )

    def _centrifuge():
        setattr(
            StaticForm,
            "centr_time",
            SelectField(
                "Centriguation Time",
                validators=[DataRequired()],
                choices=[(x.name, x.value) for x in CentrifugationTime],
            ),
        )

        setattr(
            StaticForm,
            "centr_temp",
            SelectField(
                "Centrifuge Temp",
                validators=[DataRequired()],
                choices=[(x.name, x.value) for x in ProcessingTemps],
            ),
        )

        setattr(
            StaticForm,
            "centr_weight",
            SelectField(
                "Centrifuge Weight",
                validators=[DataRequired()],
                choices=[(x.name, x.value) for x in CentrifugationWeights],
            ),
        )

        setattr(
            StaticForm, "centr_braking", BooleanField("Braking?"),
        )

    def _second_centrifuge():
        setattr(
            StaticForm,
            "sec_centr_time",
            SelectField(
                "Second Centriguation Time",
                validators=[DataRequired()],
                choices=[(x.name, x.value) for x in CentrifugationTime],
            ),
        )

        setattr(
            StaticForm,
            "sec_centr_temp",
            SelectField(
                "Second Centrifuge Temp",
                validators=[DataRequired()],
                choices=[(x.name, x.value) for x in ProcessingTemps],
            ),
        )

        setattr(
            StaticForm,
            "sec_centr_weight",
            SelectField(
                "Second Centrifuge Weight",
                validators=[DataRequired()],
                choices=[(x.name, x.value) for x in CentrifugationWeights],
            ),
        )

        setattr(
            StaticForm, "sec_centr_braking", BooleanField("Braking?"),
        )

    def _post_centrifuge():

        setattr(
            StaticForm,
            "post_centr_time",
            SelectField(
                "Second Centriguation Time",
                validators=[DataRequired()],
                choices=[(x.name, x.value) for x in CentrifugationTime],
            ),
        )

        setattr(
            StaticForm,
            "post_centr_temp",
            SelectField(
                "Second Centrifuge Temp",
                validators=[DataRequired()],
                choices=[(x.name, x.value) for x in ProcessingTemps],
            ),
        )

    if type == "FLU":
        setattr(
            StaticForm,
            "container",
            SelectField(
                "Fluid Container",
                validators=[DataRequired()],
                choices=[(x.name, x.value) for x in FluidContainer],
            ),
        )

        if steps["pre_cent"]:
            _pre_centrifuge()
        if steps["cent"]:
            _centrifuge()
        if steps["sec_cent"]:
            _second_centrifuge()
        if steps["post_cent"]:
            _post_centrifuge()

    setattr(StaticForm, "submit", SubmitField())
    return StaticForm()
