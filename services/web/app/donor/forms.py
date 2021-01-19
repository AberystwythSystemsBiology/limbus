# Copyright (C) 2019  Keiron O'Shea <keo7@aber.ac.uk>
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
    FileField,
    StringField,
    SubmitField,
    ValidationError,
    SelectField,
    BooleanField,
    DecimalField,
    DateField,
    IntegerField,
    TextAreaField,
    HiddenField,
)

# from wtforms.fields.html5 import DateField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    URL,
    Optional,
    NumberRange,
    InputRequired,
)
from .enums import (
    RaceTypes,
    BiologicalSexTypes,
    DonorStatusTypes,
    CancerStage,
    Condition,
)
from ..sample.enums import Colour
from datetime import datetime, date
import requests
from flask import url_for
from ..misc import get_internal_api_header


class DonorFilterForm(FlaskForm):

    sex = SelectField(
        "Biological Sex",
        choices=BiologicalSexTypes.choices(with_none=True),
    )
    status = SelectField("Status", choices=DonorStatusTypes.choices(with_none=True))
    race = SelectField(
        "Race",
        choices=RaceTypes.choices(with_none=True),
    )

    colour = SelectField("Colour", choices=Colour.choices())


class DoidValidatingSelectField(SelectField):
    def pre_validate(self, form):
        iri_repsonse = requests.get(
            url_for("api.doid_validate_by_iri", _external=True),
            headers=get_internal_api_header(),
            json={"iri": self.data},
        )

        if iri_repsonse.status_code != 200:
            raise ValidationError("%s is not a valid DOID iri" % (self.data))


class DonorAssignDiagnosisForm(FlaskForm):
    disease_query = StringField("Disease Query")
    disease_select = DoidValidatingSelectField("Disease Results", validators=[])
    diagnosis_date = DateField("Diagnosis Date", default=datetime.today())
    stage = SelectField("Stage", choices=CancerStage.choices())
    condition = SelectField("Condition", choices=Condition.choices())
    comments = TextAreaField("Comments")

    submit = SubmitField("Submit")


def DonorSampleAssociationForm(samples: dict):
    class StaticForm(FlaskForm):
        submit = SubmitField("Submit")

    sample_choices = []
    for sample in samples:
        sample_choices.append([sample["id"], sample["uuid"]])

    setattr(
        StaticForm, "sample", SelectField("Sample", choices=sample_choices, coerce=int)
    )

    return StaticForm()


def DonorCreationForm(sites: dict, data={}):
    site_choices = []
    for site in sites:
        site_choices.append([site["id"], "LIMBSIT-%i: %s" % (site["id"], site["name"])])

    class StaticForm(FlaskForm):
        id = StringField("id", default=None)
        colour = SelectField("Colour", choices=Colour.choices())

        month = SelectField(
            "Month",
            choices=[(str(x), x) for x in range(1, 13)],
        )
        year = SelectField("Year", choices=[(str(x), x) for x in range(2020, 1899, -1)])

        sex = SelectField(
            "Biological Sex",
            choices=BiologicalSexTypes.choices(),
        )

        mpn = StringField("Master Patient Number")

        registration_date = DateField("Registration Date", default=date.today())

        status = SelectField("Status", choices=DonorStatusTypes.choices())

        death_date = DateField("Date of Death", default=date.today(), validators=[Optional()])

        weight = StringField("Weight (kg)", default='')
        height = StringField("Height (cm)", default='')

        race = SelectField(
            "Race",
            choices=RaceTypes.choices(),
        )

        site = SelectField(
            "Site",
            description="The site in which the sample was taken",
            coerce=int,
            validators=[Optional()],
            choices=site_choices,
        )
        submit = SubmitField("Submit")

        def validate(self):
            if not FlaskForm.validate(self):
                return False
            
            if self.status.data == "DE":
                if self.death_date.data is None:
                    self.death_date.errors.append("Date required.")
                    return False

            return True

    return StaticForm(data=data)

