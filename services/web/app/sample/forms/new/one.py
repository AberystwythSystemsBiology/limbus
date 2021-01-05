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

from ....validators import validate_barcode
from ...enums import Colour, DisposalInstruction
from datetime import datetime

from wtforms import (
    SelectField,
    StringField,
    SubmitField,
    DateField,
    TextAreaField,
    TimeField
)

from wtforms.validators import DataRequired, Optional



def CollectionConsentAndDisposalForm(
    consent_templates: list,
    collection_protocols: list,
    collection_sites: list
) -> FlaskForm:
    class StaticForm(FlaskForm):
        
        colour = SelectField(
            "Colour",
            choices=Colour.choices(),
            description="Identifiable colour code for the sample.",
        )

        barcode = StringField(
            "Sample Biobank Barcode",
            validators=[validate_barcode],
            description="Enter a barcode/identifier for your sample",
        )

        collection_date = DateField(
            "Sample Collection Date",
            validators=[DataRequired()],
            description="The date in which the sample was collected.",
            default=datetime.today(),
        )

        collection_time = TimeField(
            "Sample Collection Time",
            default=datetime.now(),
            validators=[Optional()],
            description="The time at which the sample was collected.",
        )

        collection_comments = TextAreaField(
            "Collection Comments",
            description="Comments pertaining to the collection of the Sample."
        )

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

        consent_select = SelectField(
            "Patient Consent Form Template",
            validators=[DataRequired()],
            choices=consent_templates,
            description="The patient consent form template that reflects the consent form the sample donor signed.",
            coerce=int,
        )

        collection_select = SelectField(
            "Collection Protocol",
            choices=collection_protocols,
            description="The protocol that details how the sample was taken.",
            coerce=int,
        )

        collected_by = StringField(
            "Collected By",
            description="The initials of the individual who collected the sample.",
        )

        collection_site = SelectField(
            "Collection Site",
            description="The site in which the sample was taken",
            coerce=int,
            choices=collection_sites,
        )

        submit = SubmitField("Continue")

    return StaticForm()