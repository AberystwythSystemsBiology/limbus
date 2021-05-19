# Copyright (C) 2021 Keiron O'Shea <keo7@aber.ac.uk>
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
from wtforms.validators import DataRequired, Optional
from wtforms import SelectField, SubmitField, DateField, TimeField, TextAreaField
from ..enums import DisposalInstruction
from datetime import datetime

class SampleDisposalForm(FlaskForm):

    instruction = SelectField("Disposal Instructions", choices=DisposalInstruction.choices())
    comments = TextAreaField("Comments")

    date = DateField(
            "Disposal Event Date",
            validators=[DataRequired()],
            description="The date in which the disposal was undertaken.",
            default=datetime.today(),
        )

    time = TimeField(
        "Disposal Event Time",
         default=datetime.now(),
        validators=[Optional()],
        description="The time at which the disposal was undertaken.",
    )

    submit = SubmitField("Submit")

