from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import (
    SelectField,
    StringField,
    SubmitField,
    FloatField,
    DateField,
    BooleanField,
    TimeField,
    IntegerField,
)
from wtforms.validators import DataRequired, Length


from .enums import *
from ..document.models import Document, DocumentType
from ..auth.models import User
from .models import SampleDocumentAssociation
from ..patientconsentform.models import ConsentFormTemplate, ConsentFormTemplateQuestion

from ..processing.models import ProcessingTemplate
from ..processing.enums import ProtocolTypes, ProtocolSampleType

from ..storage.enums import CellContainer, FluidContainer, FixationType
from ..donor.models import Donors

from .. import db


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


def PatientConsentFormSelectForm():
    class StaticForm(FlaskForm):
        barcode = StringField("Sample Biobank Barcode")

        collection_date = DateField(
            "Sample Collection Date",
            validators=[DataRequired()],
            description="The date in which the sample was collected.",
        )

        disposal_date = DateField(
            "Disposal Date (*)",
            description="The date in which the sample is required to be disposed of in accordance to the disposal instructions.",
        )

        disposal_instruction = SelectField(
            "Disposal Instructions",
            choices=DisposalInstruction.choices(),
            description="The method of sample disposal.",
        )

        has_donor = BooleanField("Has Donor")

    donors = db.session.query(Donors).all()
    donor_choices = []
    if len(donors) == 0:
        donor_choices.append(["0", "No Suitable Donor Available"])

    for donor in donors:
        donor_choices.append([str(donor.id), "LIMBDON-%s" % (donor.id)])

    setattr(
        StaticForm,
        "donor_select",
        SelectField(
            "Sample Donor",
            choices=donor_choices,
            description="The patient consent form template that reflects the consent form the sample donor signed. ",
        ),
    )

    patient_consent_forms = db.session.query(ConsentFormTemplate).all()

    setattr(
        StaticForm,
        "form_select",
        SelectField(
            "Patient Consent Form Template",
            validators=[DataRequired()],
            choices=[
                (str(cf.id), "LIMBPCF-%s: %s" % (cf.id, cf.name))
                for cf in patient_consent_forms
            ],
            description="The patient consent form template that reflects the consent form the sample donor signed. ",
        ),
    )

    setattr(StaticForm, "submit", SubmitField())

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


def PatientConsentQuestionnaire(questions) -> FlaskForm:
    class StaticForm(FlaskForm):
        consent_id = StringField(
            "Patient Consent Form ID/Code",
            description="The identifying code of the signed patient consent form.",
        )

    for question in questions:
        setattr(StaticForm, str(question.id), BooleanField(question.question))

    setattr(StaticForm, "submit", SubmitField("Submit"))
    return StaticForm()


class FinalSampleForm:
    elements = {
        "submit": SubmitField("Submit"),
    }


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
        .filter(ProcessingTemplate.type == ProtocolTypes.ALD)
        .filter(
            ProcessingTemplate.sample_type.in_(
                [processsing_enum, ProtocolSampleType.ALL]
            )
        )
        .all()
    )

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
