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


# Step One:
def CollectionConsentAndDisposalForm(
    consent_templates: list, collection_protocols: list, collection_sites: list
) -> FlaskForm:
    class StaticForm(FlaskForm):
        def validate_barcode(form, field):
            if field.data != "":
                samples_response = requests.get(
                    url_for("api.sample_query", _external=True),
                    headers=get_internal_api_header(),
                    json={"barcode": field.data},
                )

                if samples_response.status_code == 200:
                    if len(samples_response.json()["content"]) != 0:
                        raise ValidationError("Biobank barcode must be unique!")

        sample_management_type = SelectField(
            "Sample Management Type",
            description="Choose biobank (default) or temporary storage",
            choices=[["NPR", "Biobank"], ["TMP", "Temporary storage"]],
            validators=[Optional()],
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

        has_donor = BooleanField("Has Donor")

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

class SampleTypeSelectForm(FlaskForm):

    biohazard_level = SelectField(
        "Biohazard Level",
        choices=BiohazardLevel.choices(),
        description="BSL category for the sample.",
    )

    sample_type = SelectField("Sample Type", choices=SampleType.choices())
    fluid_sample_type = SelectField(
        "Fluid Sample Type", choices=FluidSampleType.choices()
    )

    tissue_sample_type = SelectField("Tissue Type", choices=TissueSampleType.choices())

    molecular_sample_type = SelectField(
        "Molecular Sample Type", choices=MolecularSampleType.choices()
    )
    cell_sample_type = SelectField("Cell Sample Type", choices=CellSampleType.choices())

    quantity = FloatField("Quantity", validators=[DataRequired()])
    fixation_type = SelectField("Fixation Type", choices=FixationType.choices())

    fluid_container = SelectField("Fluid Container", choices=FluidContainer.choices())
    cell_container = SelectField("Cell Container", choices=CellContainer.choices())

    submit = SubmitField("Continue")




def ProtocolTemplateSelectForm(protocol_templates: list) -> FlaskForm:
    class StaticForm(FlaskForm):
        sample_status = SelectField(
            "Sample Status",
            choices=SampleStatus.choices(),
            description="The current status of the Sample.",
        )

        processing_date = DateField(
            "Processing Date",
            default=datetime.today(),
            description="The date in which the sample was processed.",
            validators=[Optional()],
        )
        processing_time = TimeField(
            "Processing Time",
            default=datetime.now(),
            description="The time in which the sample was processed.",
            validators=[Optional()],
        )

        processing_protocol_id = SelectField(
            "Processing Protocol",
            choices=protocol_templates,
            coerce=int,
            # validators=[DataRequired()],
            validators=[Optional()],
        )

        comments = TextAreaField("Comments")

        undertaken_by = StringField(
            "Processed",
            description="The initials of the individual who processed the sample.",
        )

        submit = SubmitField("Continue")

    return StaticForm()





def PatientConsentQuestionnaire(consent_template: dict) -> FlaskForm:
    class StaticForm(FlaskForm):
        consent_id = StringField(
            "Patient Consent Form ID/Code",
            description="The identifying code of the signed patient consent form.",
        )

        comments = TextAreaField("Comments")

        date_signed = DateField("Date of Consent", default=datetime.today())

        submit = SubmitField("Continue")

    for question in consent_template["questions"]:
        setattr(
            StaticForm,
            str(question["id"]),
            BooleanField(
                question["question"], render_kw={"question_type": question["type"]}
            ),
        )

    return StaticForm()


def SampleAliquotingForm(processing_templates: dict) -> FlaskForm:
    class StaticForm(FlaskForm):
        aliquot_date = DateField(
            "Aliquot Date", validators=[DataRequired()], default=datetime.today()
        )
        aliquot_time = TimeField(
            "Aliquot Time", validators=[DataRequired()], default=datetime.now()
        )
        comments = TextAreaField("Comments")
        processed_by = StringField(
            "Processed By",
            description="The initials of the individual who collected the sample.",
        )
        submit = SubmitField("Submit")

    processing_template_choices = []

    for protocol in processing_templates:
        processing_template_choices.append(
            [protocol["id"], "LIMBPRO-%i: %s" % (protocol["id"], protocol["name"])]
        )

    setattr(
        StaticForm,
        "processing_protocol",
        SelectField(
            "Processing Protocol", choices=processing_template_choices, coerce=int
        ),
    )



    setattr(
        StaticForm,
        "processed_by",
        # SelectField("Processed By", choices=user_choices, coerce=int),
        # sample processor not necessarily in the system
        StringField("Processed By"),
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

def FinalSampleForm(custom_attributes: list) -> FlaskForm:

    # TODO: Likely to be broken out to a new file
    def _custom_text_field(attribute):
        text_setting = attribute["text_setting"]

        if text_setting["type"] == "SF":
            form_type = StringField
        else:
            form_type = TextAreaField

        return form_type(
            attribute["term"],
            description=attribute["term"],
            validators=[DataRequired(), Length(max=text_setting["max_length"])],
            render_kw={"custom": True},
        )

    def _custom_numeric_field(attribute):
        return FloatField(
            attribute["term"],
            description=attribute["description"],
            validators=[DataRequired()],
            render_kw={"custom": True},
        )

    def _custom_option_field(attribute):
        choices = []
        for option in attribute["options"]:
            choices.append([option["id"], option["term"]])

        return SelectField(
            attribute["term"],
            description=attribute["description"],
            validators=[DataRequired()],
            choices=choices,
            render_kw={"custom": True},
            coerce=int,
        )

    # END TODO

    class StaticForm(FlaskForm):
        colour = SelectField(
            "Colour",
            choices=Colour.choices(),
            description="Identifiable colour code for the sample.",
        )

        comments = TextAreaField("Comments")
        submit = SubmitField("Submit")

    for attribute in custom_attributes:
        if attribute["type"] == "TEXT":
            form_element = _custom_text_field(attribute)
        elif attribute["type"] == "OPTION":
            form_element = _custom_option_field(attribute)
        else:
            form_element = _custom_numeric_field(attribute)

        setattr(StaticForm, str(attribute["id"]), form_element)

    return StaticForm()




