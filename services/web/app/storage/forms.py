from flask_wtf import FlaskForm
from wtforms import (
    PasswordField,
    StringField,
    BooleanField,
    RadioField,
    SubmitField,
    DateField,
    TimeField,
    FileField,
    ValidationError,
    SelectField,
    IntegerField,
)
from wtforms.validators import DataRequired, Email, EqualTo, URL, ValidationError
import pycountry
from ..setup.forms import post_code_validator

from .models import FixedColdStorageTemps, FixedColdStorageType


class RoomRegistrationForm(FlaskForm):
    room = StringField("Room Number", validators=[DataRequired()])
    building = StringField("Building")
    submit = SubmitField("Register Room")


class NewShelfForm(FlaskForm):
    name = StringField(
        "Shelf Name",
        validators=[DataRequired()],
        description="A descriptive name for the shelf, something like top shelf.",
    )

    description = StringField(
        "Shelf Description",
        description="A brief description of the shelf."
    )

    submit = SubmitField("Register Shelf")


def NewCryovialBoxForm():
    class StaticForm(FlaskForm):
        serial = StringField("Serial Number", validators=[DataRequired()])
        num_rows = IntegerField("Number of Rows", validators=[DataRequired()])
        num_cols = IntegerField("Number of Columns", validators=[DataRequired()])

    setattr(StaticForm, "submit", SubmitField("Register Cryovial Box"))

    return StaticForm()


class NewCryovialBoxFileUploadForm(FlaskForm):
    serial = StringField("Serial Number", validators=[DataRequired()])
    file = FileField("File", validators=[DataRequired()])
    submit = SubmitField("Upload File")


class SiteRegistrationForm(FlaskForm):
    name = StringField("Site Name", validators=[DataRequired()])
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
        "Post Code", validators=[DataRequired(), post_code_validator]
    )

    submit = SubmitField("Register Site")


def LongTermColdStorageForm():
    class StaticForm(FlaskForm):
        serial_number = StringField(
            "Serial Number",
            description="Equipment serial number is a serial number that identifies an equipment used in the measuring by its serial number.",
        )
        manufacturer = StringField(
            "Manufacturer",
            validators=[DataRequired()],
            description="The storage facility manufacturer.",
        )
        temperature = SelectField(
            "Temperature",
            choices=FixedColdStorageTemps.choices(),
            validators=[DataRequired()],
            description="The temperature of the inside of the storage facility.",
        )
        type = SelectField(
            "Storage Type",
            choices=FixedColdStorageType.choices(),
            validators=[DataRequired()],
            description="A facility that provides storage for any type of biospecimen and/or biospecimen container.",
        )

    setattr(StaticForm, "submit", SubmitField("Register"))

    return StaticForm()


def SampleToEntityForm(samples: list) -> FlaskForm:
    class StaticForm(FlaskForm):
        date = DateField("Entry Date", validators=[DataRequired()])
        time = TimeField("Entry Time", validators=[DataRequired()])
        entered_by = StringField("Entered By", description="The initials of the person that entered the sample.")
        submit = SubmitField("Submit Sample")


    samples_choices = []

    for sample in samples:
        samples_choices.append(
            [str(sample.id), "LIMBSMP-%s (%s)" % (sample.id, sample.sample_type)]
        )

    setattr(
        StaticForm,
        "samples",
        SelectField("Sample", choices=samples_choices, validators=[DataRequired()]),
    )

    return StaticForm()


def BoxToShelfForm(boxes: list) -> FlaskForm:
    class StaticForm(FlaskForm):
        submit = SubmitField("Submit")

    choices = []

    for box in boxes:
        choices.append([box.id, "LIMCRB-%s (Serial: %s)" % (box.id, box.serial)])

    setattr(
        StaticForm, "boxes", SelectField("Cryovial Box", choices=choices, coerce=int)
    )

    return StaticForm()


def CryoBoxFileUploadSelectForm(sample_data: dict):
    class StaticForm(FlaskForm):
        submit = SubmitField("Submit Cryovial Box")

    for position, info in sample_data.items():
        setattr(
            StaticForm,
            position,
            BooleanField(
                position,
                render_kw={
                    "_selectform": True,
                    "_has_sample": info["sample"] != None,
                    "_sample": info["sample"],
                },
            ),
        )

    return StaticForm()
