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
    TextAreaField,
    TimeField,
    FloatField
)

from wtforms.validators import DataRequired, Optional, NumberRange
from datetime import datetime


def ProtocolEventForm(protocols: list, data={}):

    class StaticForm(FlaskForm):
        protocol_id = SelectField("Protocol", choices=protocols, coerce=int)

        date = DateField(
            "Protocol Event Date",
            validators=[DataRequired()],
            description="The date in which the protocol was undertaken.",
            default=datetime.today(),
        )

        time = TimeField(
            "Protocol Event Time",
            default=datetime.now(),
            validators=[Optional()],
            description="The time at which the protocol was undertaken.",
        )

        comments = TextAreaField(
            "Comments",
        )

        undertaken_by = StringField(
            "Undertaken By",
            description="The initials of the individual who undertook the event.",
        )

        submit = SubmitField("Submit")

    try:
        metric = "ml"
        if data["base_type"] == "CEL":
            metric = "qty"

        setattr(
            StaticForm,
            "reduced_quantity",
            FloatField(
                label = "Reduction in Sample Quantity",
                description = "Quantity Reduced from the event (%s)" %metric,
                default = 0,
                validators = [Optional(), NumberRange(0, data["remaining_quantity"])]
            ),
        )
        setattr(
            StaticForm,
            "remaining_quantity",
            FloatField(
                label = "Remaining Quantity",
                description="Original quantity (%s %s)" % (data["quantity"], metric),
                render_kw={'readonly': True},
                validators = [NumberRange(0, data["remaining_quantity"])]
            ),
        )

    except:
        pass

    return StaticForm(data=data)
