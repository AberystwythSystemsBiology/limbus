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
from flask_wtf.file import FileField
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
from wtforms.validators import DataRequired, NumberRange
from datetime import datetime
from ...sample.enums import Colour


class NewSampleRackForm(FlaskForm):
    serial = StringField("Serial Number", validators=[DataRequired()])
    num_rows = IntegerField(
        "Number of Rows",
        validators=[DataRequired(), NumberRange(1, None, None)],
        default=1,
    )
    num_cols = IntegerField(
        "Number of Columns",
        validators=[DataRequired(), NumberRange(1, None, None)],
        default=1,
    )
    description = TextAreaField("Description")
    colours = SelectField("Colour", choices=Colour.choices())
    entry = StringField("Entry by", validators=[DataRequired()])
    submit = SubmitField("Register")


def EditSampleRackForm(sites: list, shelves: list, data={}):
    #site_choices = [(0, "-- Select a storage site --")] + sites


    if len(shelves) == 0:
        data["shelf_required"] = False
    else:
        # for shelf in shelves:
        #     shelf_choices.append(
        #         (shelf["id"], "LIMBSHLF-%i: %s" % (shelf["id"], shelf["name"]))
        #     )
        data["shelf_required"] = True

    shelves = [(0, "-- Select cold storage shelf --")] + shelves

    class StaticForm(FlaskForm):
        serial = StringField("Serial Number", validators=[DataRequired()])
        num_rows = IntegerField(
            "Number of Rows", validators=[DataRequired()], default=1
        )
        num_cols = IntegerField(
            "Number of Columns", validators=[DataRequired()], default=1
        )
        description = TextAreaField("Description")
        colours = SelectField("Colour", choices=Colour.choices())

        storage_id = HiddenField("Entity to storage id")
        shelf_required = BooleanField("Shelf located or not")

        site_id = SelectField(
            "Site",
            choices=sites,
            validators=[DataRequired()],
            description="The site where the shelf is located.",
            coerce=int,
            render_kw={"class": "form-control"} #bd-light"}
        )

        shelf_id = SelectField(
            "Shelf",
            choices=shelves,
            validators=[DataRequired()],
            description="The shelf where the rack is located.",
            coerce=int,
            render_kw={"class": "form-control"}# bd-light"}

        )

        submit = SubmitField("Register")

    print(str(StaticForm(data=data).data))
    return StaticForm(data=data)


def EditRackToShelfForm(shelves: list) -> FlaskForm:
    class StaticForm(FlaskForm):
        date = DateField(
            "Entry Date", validators=[DataRequired()], default=datetime.today()
        )
        time = TimeField(
            "Entry Time", validators=[DataRequired()], default=datetime.now()
        )
        entered_by = StringField(
            "Entered By",
            description="The initials of the person that entered the sample.",
        )
        submit = SubmitField("Submit")

    shelf_choices = []
    for shelf in shelves:
        shelf_choices.append(
            (shelf["id"], "LIMBSHLF-%i: %s" % (shelf["id"], shelf["name"]))
        )

    setattr(
        StaticForm,
        "shelf_id",
        SelectField("Cold Storage Shelf", choices=shelf_choices, coerce=int),
    )

    return StaticForm()


def CryoBoxFileUploadSelectForm(sample_data: dict, data={}):
    class StaticForm(FlaskForm):
        num_rows = IntegerField("Number of Rows", validators=[DataRequired()])
        num_cols = IntegerField("Number of Columns", validators=[DataRequired()])

        submit = SubmitField("Submit Cryovial Box")
    print("sample_data form", sample_data)
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
    num_rows = IntegerField("Number of Rows", default=8, validators=[DataRequired()])
    num_cols = IntegerField("Number of Columns", default=12, validators=[DataRequired()])

    barcode_type = SelectField(
        "Barcode Type",
        choices=[("barcode", "Biobank Barcode"), ("uuid", "LImBuS UUID")],
        description="The barcode attribute to cross reference against.",
    )
    file = FileField("File", validators=[DataRequired()])

    # entry_datetime = StringField("Entry by")
    entry_date = DateField(
        "Sample Rack Creation Date",
        validators=[DataRequired()],
        default=datetime.today(),
    )

    entry_time = TimeField(
        "Sample Rack Creation Time",
        default=datetime.now(),
        validators=[DataRequired()],
    )

    entry = StringField(
        "Created by",
        description="The initials of the individual who created the sample rack",
    )

    submit = SubmitField("Upload File")


class UpdateRackFileUploadForm(FlaskForm):
    # serial = StringField("Serial Number", validators=[DataRequired()])
    # description = TextAreaField("Description")
    # colour = SelectField("Colour", choices=Colour.choices())
    # num_rows = IntegerField("Number of Rows", default=8, validators=[DataRequired()])
    # num_cols = IntegerField("Number of Columns", default=12, validators=[DataRequired()])

    barcode_type = SelectField(
        "Barcode Type",
        choices=[("barcode", "Biobank Barcode"), ("uuid", "LImBuS UUID")],
        description="The barcode attribute to cross reference against.",
    )
    file = FileField("File", validators=[DataRequired()])

    # entry_datetime = StringField("Entry by")
    entry_date = DateField(
        "Sample Rack Creation Date",
        validators=[DataRequired()],
        default=datetime.today(),
    )

    entry_time = TimeField(
        "Sample Rack Creation Time",
        default=datetime.now(),
        validators=[DataRequired()],
    )

    entry = StringField("Created by",
                        description="The initials of the individual who created the sample rack",
                        validators=[DataRequired()])

    submit = SubmitField("Upload File")
