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

from ..storage.enums import CellContainer, FluidContainer, FixationType


class SampleTypeSelectForm(FlaskForm):

    sample_type = SelectField("Sample Type", choices=SampleType.choices())
    fluid_sample_type = SelectField(
        "Fluid Sample Type", choices=FluidSampleType.choices()
    )
    molecular_sample_type = SelectField(
        "Molecular Sample Type", choices=MolecularSampleType.choices()
    )
    cell_sample_type = SelectField("Cell Sample Type", choices=CellSampleType.choices())

    quantity = FloatField("Quantity", validators=[DataRequired()])
    fixation_type = SelectField("Fixation Type", choices=FixationType.choices())

    fluid_container = SelectField("Fluid Container", choices=FluidContainer.choices())
    cell_container = SelectField("Cell Container", choices=CellContainer.choices())

    submit = SubmitField("Submit")


def CollectionConsentAndDisposalForm(consent_templates: list, collection_protocols: list) -> FlaskForm:

    class StaticForm(FlaskForm):
        # TODO: Write a validator to check if Sample not already in biobank.
        barcode = StringField(
            "Sample Biobank Barcode",
            description="If your sample already has a barcode/identifier, you can enter it here."
        )

        collection_date = DateField(
            "Sample Collection Date",
            validators=[DataRequired()],
            description="The date in which the sample was collected.",
            default=datetime.today
        )

        disposal_date = DateField(
            "Sample Disposal Date (*)",
            description="The date in which the sample is required to be disposed of.",
            default=datetime.today
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
                coerce=int
        )

        collection_select = SelectField(
            "Collection Protocol",
            validators=[DataRequired()],
            choices=collection_protocols,
            description="The protocol that details how the sample was taken.",
            coerce=int
        )

        collected_by = StringField(
            "Collected By",
            description="The initials of the individual who collected the sample."
        )

        submit = SubmitField("Submit")

    return StaticForm()


def ProtocolTemplateSelectForm(templates):
    class StaticForm(FlaskForm):
        sample_status = SelectField("Sample Status", choices=SampleStatus.choices())
        processing_date = DateField("Processing Date")
        processing_time = TimeField("Processing Time")

        submit = SubmitField("Submit")

    choices = []

    for t in templates:
        choice = " LIMBPRO-%s: %s" % (t.id, t.name)
        choices.append([str(t.id), choice])

    setattr(
        StaticForm,
        "form_select",
        SelectField(
            "Processing Protocol Template", validators=[DataRequired()], choices=choices
        ),
    )

    return StaticForm()


def PatientConsentQuestionnaire(consent_template: dict) -> FlaskForm:
    class StaticForm(FlaskForm):
        consent_id = StringField(
            "Patient Consent Form ID/Code",
            description="The identifying code of the signed patient consent form.",
        )

        comments = TextAreaField(
            "Comments"
        )

        date_signed = DateField(
            "Date of Consent",
            default=datetime.today()
        )

        submit = SubmitField("Submit")

    for question in consent_template["questions"]:
        setattr(
            StaticForm,
            str(question["id"]),
            BooleanField(
                question["question"],
                render_kw={"question_type": question["type"]}
            )
        )

    return StaticForm()


class FinalSampleForm:
    elements = {
        "submit": SubmitField("Submit"),
    }

'''

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
'''