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
    SelectField,
    StringField,
    SubmitField,
    DateField,
    TimeField,
    TextAreaField,
    BooleanField,
    HiddenField,
)
from wtforms.validators import Optional

from ..enums import SampleQuality, ReviewType, ReviewResult, DisposalInstruction
from datetime import datetime


def SampleReviewForm(data={}):
    class StaticForm(FlaskForm):

        review_type = SelectField("Review Type", choices=ReviewType.choices())

        result = SelectField("Review Result", choices=ReviewResult.choices())

        quality = SelectField(
            "Sample Quality",
            choices=SampleQuality.choices(),
            description="The relative quality of the Sample.",
        )

        date = DateField(
            "Review Date",
            description="The date in which the Sample Review was undertaken.",
            default=datetime.today(),
        )
        time = TimeField(
            "Review Time",
            description="The time in which the Sample Review was undertaken.",
            default=datetime.now(),
        )
        conducted_by = StringField(
            "Review Conducted By",
            description="Initials of the individual who undertook the Sample Review.",
        )

        comments = TextAreaField("Comments", description="Any relevant observations.")

        disposal_edit_on = BooleanField("", default=False)

        disposal_date = DateField(
            "Sample Disposal Date (*)",
            description="The date in which the sample is required to be disposed of.",
            default=datetime.today,
            validators=[Optional()],
        )

        disposal_instruction = SelectField(
            "Sample Disposal Instruction",
            choices=DisposalInstruction.choices(),
            description="The method of sample disposal.",
            validators=[Optional()],
        )

        disposal_comments = TextAreaField("Sample Disposal Comments")
        # approved_by = TextAreaField("To be approved by ")

        submit = SubmitField("Submit")

        def validate(self):
            if not FlaskForm.validate(self):
                return False

            if self.disposal_edit_on.data:
                if self.disposal_instruction.data in ["DES", "TRA"]:
                    if self.disposal_date.data is None:
                        self.disposal_date.errors.append(
                            "Expected disposal date required."
                        )
                        self.review_type.errors.append(
                            "Disposal instruction edit error! Expected action date required!!"
                        )
                        return False

            return True

    return StaticForm(data=data)
