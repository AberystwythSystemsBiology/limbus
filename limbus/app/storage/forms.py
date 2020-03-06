from flask_wtf import FlaskForm
from wtforms import (
    PasswordField,
    StringField,
    SubmitField,
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
    submit = SubmitField("Register Shelf")


class NewCryovialBoxForm(FlaskForm):
    serial = StringField("Serial Number", validators=[DataRequired()])
    num_rows = IntegerField("Number of Rows", validators=[DataRequired()])
    num_cols = IntegerField("Number of Columns", validators=[DataRequired()])
    submit = SubmitField("Register Cryovial Box")


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
        "Post Code", validators=[DataRequired(), post_code_validator],
    )

    submit = SubmitField("Register Site")


def LongTermColdStorageForm(rs_query):
    class StaticForm(FlaskForm):
        serial_number = StringField("Serial Number")
        manufacturer = StringField("Manufacturer", validators=[DataRequired()])
        temperature = SelectField(
            "Temperature",
            choices=FixedColdStorageTemps.choices(),
            validators=[DataRequired()],
        )
        type = SelectField(
            "Storage Type",
            choices=FixedColdStorageType.choices(),
            validators=[DataRequired()],
        )

    site_choices = []

    for index, (room, site) in enumerate(rs_query):
        site_choices.append(
            [str(index), "Room %s in %s" % (room.room_number, site.name)]
        )

    location = SelectField(
        "Location", choices=site_choices, validators=[DataRequired()]
    )

    setattr(StaticForm, "location", location)
    setattr(StaticForm, "submit", SubmitField("Register Long Term Cold Storage"))

    return StaticForm()
