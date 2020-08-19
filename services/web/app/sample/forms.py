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
from wtforms.validators import DataRequired, Length

from datetime import datetime

from .enums import *


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
            validators=[DataRequired(), Length(text_setting["max_length"])],
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
            description=
            "Identifiable colour code for the sample.",
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


def CollectionConsentAndDisposalForm(
    consent_templates: list, collection_protocols: list, collection_sites: list
) -> FlaskForm:
    class StaticForm(FlaskForm):
        # TODO: Write a validator to check if Sample not already in biobank.
        barcode = StringField(
            "Sample Biobank Barcode",
            description="If your sample already has a barcode/identifier, you can enter it here.",
        )

        collection_date = DateField(
            "Sample Collection Date",
            validators=[DataRequired()],
            description="The date in which the sample was collected.",
            default=datetime.today,
        )

        collection_time = TimeField(
            "Sample Collection Time",
            default=datetime.now(),
            validators=[DataRequired()],
            description="The time at which the sample was collected.",
        )

        disposal_date = DateField(
            "Sample Disposal Date (*)",
            description="The date in which the sample is required to be disposed of.",
            default=datetime.today,
        )

        disposal_instruction = SelectField(
            "Sample Disposal Instruction",
            choices=DisposalInstruction.choices(),
            description="The method of sample disposal.",
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
            validators=[DataRequired()],
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
            validators=[DataRequired()],
            choices=collection_sites,
        )

        submit = SubmitField("Continue")

    return StaticForm()


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
        )
        processing_time = TimeField(
            "Processing Time",
            default=datetime.now(),
            description="The time in which the sample was processed.",
        )

        processing_protocol_id = SelectField(
            "Processing Protocol",
            choices=protocol_templates,
            coerce=int,
            validators=[DataRequired()],
        )

        comments = TextAreaField("Comments")

        undertaken_by = StringField(
            "Processed",
            description="The initials of the individual who processed the sample.",
        )

        submit = SubmitField("Continue")

    return StaticForm()


class SampleReviewForm(FlaskForm):
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


"""

def SampleAliquotingForm(sample_type, default_type) -> FlaskForm:
    class StaticForm(FlaskForm):
        count = IntegerField("Aliquot Count", validators=[DataRequired()])
        size = StringField(
            "Sample Quantity per Aliquot", validators=[DataRequired(), Length(min=1)]
        )
        use_entire = BooleanField("Use all of Parent Sample?")
        aliquot_date = DateField("Aliquot Date", validators=[DataRequired()])
        aliquot_time = TimeField("Aliquot Time", validators=[DataRequired()])
        cell_viability = IntegerField("Cell Viability %")
        lock_parent = BooleanField("Lock Parent?")

        submit = SubmitField("Submit")

    if sample_type == SampleType.FLU:
        sample_type_enums = FluidSampleType
        processsing_enum = ProtocolSampleType.FLU
    elif sample_type == SampleType.CEL:
        sample_type_enums = CellSampleType
        processsing_enum = ProtocolSampleType.CEL

    else:
        sample_type_enums = MolecularSampleType
        processsing_enum = ProtocolSampleType.MOL

    _ec = sample_type_enums.choices()

    setattr(StaticForm, "sample_type", SelectField("Sample Type", choices=_ec))


    processing_templates = (
        db.session.query(ProcessingTemplate)
        .filter(ProcessingTemplate.type == ProtocolType.ALD)
        .filter(
            ProcessingTemplate.sample_type.in_(
                [processsing_enum, ProtocolSampleType.ALL]
            )
        )
        .all()
    )
   

    protcessing_templates = {}

    setattr(
        StaticForm,
        "processing_template",
        SelectField(
            "Processing Template (Aliquot)",
            coerce=int,
            choices=[
                (x.id, "LIMBPRO-%i: %s" % (x.id, x.name)) for x in processing_templates
            ],
        ),
    )

    return StaticForm(), len(processing_templates)
"""
