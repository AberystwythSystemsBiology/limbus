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
)
from ..enums import SampleQuality, ReviewType, ReviewResult
from datetime import datetime


class SampleReviewForm(FlaskForm):

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
    submit = SubmitField("Submit")
