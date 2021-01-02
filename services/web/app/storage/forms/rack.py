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
    BooleanField
)

from wtforms.validators import DataRequired

from ...sample.enums import Colour

class NewSampleRackForm(FlaskForm):
    serial = StringField("Serial Number", validators=[DataRequired()])
    num_rows = IntegerField("Number of Rows", validators=[DataRequired()], default=1)
    num_cols = IntegerField("Number of Columns", validators=[DataRequired()], default=1)
    description = TextAreaField("Description")
    colours = SelectField("Colour", choices=Colour.choices())
    submit = SubmitField("Register")


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
                    "_sample": info,
                },
            ),
        )

    return StaticForm()



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
    submit = SubmitField("Upload File")

