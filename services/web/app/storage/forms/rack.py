# Copyright (C) 2020 Keiron O'Shea <keo7@aber.ac.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    IntegerField,
    SelectField,
    TextAreaField,
    FileField,
    BooleanField,
    HiddenField,
    DateField,
    TimeField,
)

from wtforms.validators import DataRequired
from datetime import datetime
from ...sample.enums import Colour


class NewSampleRackForm(FlaskForm):
    serial = StringField("Serial Number", validators=[DataRequired()])
    num_rows = IntegerField("Number of Rows", validators=[DataRequired()], default=1)
    num_cols = IntegerField("Number of Columns", validators=[DataRequired()], default=1)
    description = TextAreaField("Description")
    colours = SelectField("Colour", choices=Colour.choices())
    entry = StringField("Entry by")
    submit = SubmitField("Register")


def EditSampleRackForm(shelves: list, data={}):
    shelf_choices = []

    if (len(shelves) == 0):
        data["shelf_required"] = False
    else:
        for shelf in shelves:
            shelf_choices.append((shelf["id"], "LIMBSHLF-%i: %s" % (shelf["id"], shelf["name"])))
        data["shelf_required"] = True

    class StaticForm(FlaskForm):
        serial = StringField("Serial Number", validators=[DataRequired()])
        num_rows = IntegerField("Number of Rows", validators=[DataRequired()], default=1)
        num_cols = IntegerField("Number of Columns", validators=[DataRequired()], default=1)
        description = TextAreaField("Description")
        colours = SelectField("Colour", choices=Colour.choices())

        storage_id = HiddenField("Entity to storage id")
        shelf_required = BooleanField('Shelf located or not')
        shelf_id = SelectField(
            "Shelf",
            choices=shelf_choices,
            validators=[DataRequired()],
            description="The shelf where the rack is located.", coerce=int,
        )

        submit = SubmitField("Register")

    return StaticForm(data=data)



def CryoBoxFileUploadSelectForm(sample_data: dict, data={}):
    class StaticForm(FlaskForm):
        num_rows = IntegerField("Number of Rows", validators=[DataRequired()])
        num_cols = IntegerField("Number of Columns", validators=[DataRequired()])

        submit = SubmitField("Submit Cryovial Box")

    for position, info in sample_data.items():
        setattr(
            StaticForm,
            position,
            BooleanField(
                position,
                render_kw={
                    "_selectform": True,
                    "_sample": info,
                },
            ),
        )

    return StaticForm(data=data)


class NewCryovialBoxFileUploadForm(FlaskForm):
    serial = StringField("Serial Number", validators=[DataRequired()])
    description = TextAreaField("Description")
    colour = SelectField("Colour", choices=Colour.choices())
    barcode_type = SelectField(
        "Barcode Type",
        choices=[("uuid", "LImBuS UUID"), ("biobank_barcode", "Biobank Barcode")],
        description="The barcode attribute to cross reference against.",
    )
    file = FileField("File", validators=[DataRequired()])

    #entry_datetime = StringField("Entry by")
    entry_date = DateField(
        "Sample Rack Creation Date",
        validators=[DataRequired()],
        #description="The date in which the sample rack was created.",
        default=datetime.today(),
    )

    entry_time = TimeField(
        "Sample Rack Creation Time",
        default=datetime.now(),
        validators=[DataRequired()],
        #description="The time at which the sample rack was undertaken.",
    )

    entry = StringField("Created by",
        description = "The initials of the individual who created the sample rack"
    )

    submit = SubmitField("Upload File")
