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


from flask import url_for
from flask_wtf import FlaskForm
from wtforms import (
    SelectField,
    StringField,
    TextAreaField,
    SubmitField,
    FloatField,
    DateField,
    BooleanField,
    TimeField,
    IntegerField,
)
from wtforms.validators import DataRequired, Length, ValidationError, Optional
from wtforms.widgets import TextInput

from datetime import datetime

from ..enums import *
import requests
from ...misc import get_internal_api_header
from ...validators import validate_barcode


def SampleAliquotingForm(aliquot_protocols=[]) -> FlaskForm:
    class StaticForm(FlaskForm):
        aliquot_date = DateField(
            "Aliquot Date", validators=[DataRequired()], default=datetime.today()
        )
        aliquot_time = TimeField(
            "Aliquot Time", validators=[DataRequired()], default=datetime.now()
        )
        comments = TextAreaField("Comments")
        container_base_type = SelectField(
            "Container base type", choices=ContainerBaseType.choices(), default="LTS"
        )

        processed_by = StringField(
            "Processed By",
            description="The initials of the individual who collected the sample.",
        )
        submit = SubmitField("Submit")

    setattr(
        StaticForm,
        "processing_protocol",
        SelectField("Processing Protocol", choices=aliquot_protocols, coerce=int),
    )

    setattr(
        StaticForm,
        "processed_by",
        # SelectField("Processed By", choices=user_choices, coerce=int),
        # sample processor not necessarily in the system
        StringField("Processed By"),
    )

    return StaticForm()


def SampleDerivationForm(processing_protocols=[], derivation_protocols=[]) -> FlaskForm:
    class StaticForm(FlaskForm):
        processing_date = DateField(
            "Processing Date", validators=[DataRequired()], default=datetime.today()
        )
        processing_time = TimeField(
            "Processing Time", validators=[DataRequired()], default=datetime.now()
        )
        processing_comments = TextAreaField("Comments on processing")

        processed_by = StringField(
            "Processed By",
            description="The initials of the individual who processed the sample.",
        )

        derivation_date = DateField(
            "Derivation Date", validators=[DataRequired()], default=datetime.today()
        )
        derivation_time = TimeField(
            "Derivation Time", validators=[DataRequired()], default=datetime.now()
        )
        derivation_comments = TextAreaField("Comments on derivation")

        derived_by = StringField(
            "Derived By",
            description="The initials of the individual who processed the sample.",
        )

        submit = SubmitField("Submit")

    setattr(
        StaticForm,
        "processing_protocol",
        SelectField("Processing Protocol", choices=processing_protocols, coerce=int),
    )

    setattr(
        StaticForm,
        "derivation_protocol",
        SelectField(
            "Derivation/Aliquot Protocol", choices=derivation_protocols, coerce=int
        ),
    )

    return StaticForm()


def CustomAttributeSelectForm(custom_attributes: dict) -> FlaskForm:
    class StaticForm(FlaskForm):
        submit = SubmitField("Submit")

    for attribute in custom_attributes:
        setattr(
            StaticForm,
            str(attribute["id"]),
            BooleanField(attribute["term"], render_kw={"attribute": attribute}),
        )

    return StaticForm()


def EditBasicForm(consent_ids: list, collection_sites: list, data: {}) -> FlaskForm:

    if "status" in data:
        # - Find a match either in the type or the expression value
        data["status"] = SampleStatus(data["status"]).name

    if "biohazard_level" in data:
        # - Find a match either in the type or the expression value
        data["biohazard_level"] = BiohazardLevel(data["biohazard_level"]).name

    if "colour" in data:
        data["colour"] = Colour(data["colour"]).name

    class StaticForm(FlaskForm):

        status = SelectField("Sample Status", choices=SampleStatus.choices())

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

        biohazard_level = SelectField(
            "Biohazard Level",
            choices=BiohazardLevel.choices(),
            description="BSL category for the sample.",
        )

        quantity = FloatField("Quantity", validators=[DataRequired()])

        # remaining_quantity = FloatField("Remaining Quantity", validators=[DataRequired()])

        consent_id = SelectField(
            "Donor Consent ID",
            validators=[DataRequired()],
            choices=consent_ids,
            description="The associated consent that the sample donor signed.",
            coerce=int,
        )

        site_id = SelectField(
            "Collection Site",
            description="The site in which the sample was taken",
            coerce=int,
            choices=collection_sites,
        )

        submit = SubmitField("Save Changes")

        def validate(self):
            if not FlaskForm.validate(self):
                return False

            if self.status.data in ["DES", "TRA"]:
                if "status" in data:
                    if data["status"] != self.status.data:
                        self.status.errors.append(
                            "Sample status can be set to destroyed/transferred via sample disposal/shipment event only"
                        )
                        return False
                else:
                    self.status.errors.append(
                        "Sample status can't be changed in case of destroyed/transferred"
                    )
                    return False

            return True

    return StaticForm(data=data)
