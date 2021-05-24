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
from wtforms import SelectField, StringField, SubmitField, BooleanField
from ..enums import Colour, BiohazardLevel, SampleSource, SampleStatus, SampleBaseType


class SampleFilterForm(FlaskForm):

    biohazard_level = SelectField(
        "Biohazard Level", choices=BiohazardLevel.choices(with_none=True)
    )

    uuid = StringField("UUID")
    barcode = StringField("Barcode")
    colour = SelectField("Colour", choices=Colour.choices(with_none=True))
    type = SelectField("Sample Type", choices=SampleBaseType.choices(with_none=True))
    source = SelectField("Sample Source", choices=SampleSource.choices(with_none=True))
    status = SelectField("Sample Status", choices=SampleStatus.choices(with_none=True))
    submit = SubmitField("Filter")
