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
    FieldList,
    FormField
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

        death_date = DateField(
            "Date of Death", default=date.today(), validators=[Optional()]
        )

        weight = StringField("Weight (kg)", default="")
        height = StringField("Height (cm)", default="")

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



def ConsentTemplateSelectForm(consent_templates: list) -> FlaskForm:
    class StaticForm(FlaskForm):

        consent_select = SelectField(
            "Donor Consent Form Template",
            validators=[DataRequired()],
            choices=consent_templates,
            description="The consent form template that reflects the consent form the sample donor signed.",
            coerce=int,
        )

        submit = SubmitField("Continue")

    return StaticForm()




def ConsentQuestionnaire(data={})-> FlaskForm:

    class StaticForm(FlaskForm):

        template_name = TextAreaField("template_name")

        template_version = StringField("version")

        identifier = StringField(
            "Donor Consent Form ID/Code",
            description="The identifying code of the signed patient consent form.",
        )

        comments = TextAreaField("Comments")

        date = DateField("Date of Consent", default=datetime.today())

        submit = SubmitField("Continue")

    for question in data["questions"]:
        setattr(
            StaticForm,
            str(question["id"]),
            BooleanField(
                question["question"], render_kw={"question_type": question["type"]}
            ),
        )

    return StaticForm(data=data)


class ConsentAnswerForm(FlaskForm):
    question = TextAreaField(
        "Consent Item",
        description="The item that has been consented.",
    )
    answer = BooleanField("Consented", default="checked")

def DonorConsentForm(data={}):
    class StaticForm(FlaskForm):

        template_name = TextAreaField(
            "Consent Comments",
            description="Comments related to the consent.",
        )

        template_version = StringField("identifier")

        consent_date = DateField(
            "Date of consent",
            validators=[DataRequired()],
            description="The date in which the consent form was signed.",
            default=datetime.today(),
        )

        identifier = StringField("identifier")
        questionnaire = FieldList(FormField(ConsentAnswerForm))

        comments = TextAreaField(
            "Consent Comments",
            description="Comments related to the consent.",
        )

        submit = SubmitField("Submit")

    return StaticForm(data=data)



def CollectionDonorConsentAndDisposalForm0(
    consent_ids: list, collection_protocols: list, collection_sites: list, data={}
) -> FlaskForm:
    print('consent_ids', consent_ids)
    print("coll protol", collection_protocols)
    class StaticForm(FlaskForm):
        donor_id = HiddenField("Donor id")

        sample_status = SelectField("Sample Status", choices=SampleStatus.choices())

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
            description="Comments pertaining to the collection of the Sample.",
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

        disposal_comments = TextAreaField("Sample Disposal Comments")

        consent_id = SelectField(
            "Donor Consent ID",
            validators=[DataRequired()],
            choices=consent_ids,
            description="The associated consent that the sample donor signed.",
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
