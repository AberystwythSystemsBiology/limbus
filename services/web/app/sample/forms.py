from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import (
    SelectField,
    StringField,
    SubmitField,
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

from .. import db

class SampleTypeSelectForm(FlaskForm):
    sample_type = SelectField("Sample Type", choices=SampleType.choices())
    barcode = StringField("Biobank Barcode")

    fluid_sample_type = SelectField("Fluid Sample Type", choices=FluidSampleType.choices())
    molecular_sample_type = SelectField("Molecular Sample Type", choices=MolecularSampleType.choices())
    cell_sample_type = SelectField("Cell Sample Type", choices=CellSampleType.choices())
    quantity = StringField("Quantity")

    cell_container = SelectField("Cell Container", choices=CellContainer.choices())
    fixation_type = SelectField("Fixation Type", choices=FixationType.choices())

    fluid_container = SelectField("Fluid Container", choices=FluidContainer.choices())

    submit = SubmitField("Submit")

class SampleCreationForm(FlaskForm):
    collection_date = DateField("Sample Collection Date", validators=[DataRequired()])
    disposal_instruction = SelectField("Disposal Instructions", choices=DisposalInstruction.choices())
    disposal_date = DateField("Disposal Date")


def PatientConsentFormSelectForm():
    class StaticForm(FlaskForm):
        consent_id = StringField("Patient Consent Identifier")

    length = 0

    patient_consent_forms = (
        db.session.query(ConsentFormTemplate, User)
        .filter(ConsentFormTemplate.uploader == User.id)
        .all()
    )

    choices = []

    for cf, user in patient_consent_forms:
        id = cf.id
        length += 1
        choice = " LIMBPCF-%s: %s" % (cf.id, cf.name)
        choices.append([str(id), choice])

    setattr(
        StaticForm,
        "form_select",
        SelectField(
            "Patient Consent Form Template",
            validators=[DataRequired()],
            choices=choices,
        ),
    )

    setattr(StaticForm, "submit", SubmitField())

    return StaticForm(), length


# TODO: Duplicate Code
def ProtocolTemplateSelectForm(templates):
    class StaticForm(FlaskForm):
        sample_status = SelectField("Sample Status", choices=SampleStatus.choices())
        processing_time = TimeField("Processing Time", default=datetime.today)
        processing_date = DateField("Processing Date")
        submit = SubmitField("Submit")

    length = len(templates)
    choices = []


    for t in templates:
        choice = " LIMBPRO-%s: %s" % (t.id, t.name)
        choices.append([str(t.id), choice])

    setattr(
        StaticForm,
        "form_select",
        SelectField(
            "Processing Protocol Template",
            validators=[DataRequired()],
            choices=choices,
        ),
    )



    return StaticForm(), length


def PatientConsentQuestionnaire(questions) -> FlaskForm:
    class StaticForm(FlaskForm):
        pass

    for question in questions:
        setattr(
            StaticForm, str(question.id), BooleanField(question.question)
        )

    # Inject submit

    setattr(StaticForm, "submit", SubmitField("Submit"))
    return StaticForm()



class FinalSampleForm:
    elements = {
        "collection_date": DateField("Collection Date", validators=[DataRequired()]),
        "disposal_instruction": SelectField("Disposal Instructions", choices=DisposalInstruction.choices()),
        "disposal_date" : DateField("Disposal Date"),
        "submit": SubmitField("Submit")
    }



def SampleAliquotingForm(sample_type, default_type) -> FlaskForm:


    class StaticForm(FlaskForm):
        count = IntegerField("Aliquot Count", validators=[DataRequired()])
        size = StringField("Sample Quantity per Aliquot", validators=[DataRequired(), Length(min=1)])
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
    _i = [i for i, x in enumerate(_ec) if x[1] == default_type][0]
    _ec.insert(0, _ec.pop(_i))

    setattr(
        StaticForm,
        "sample_type",
        SelectField("Sample Type", choices=_ec)
    )

    processing_templates = db.session.query(ProcessingTemplate).filter(
        ProcessingTemplate.type == ProtocolTypes.ALD
    ).filter(ProcessingTemplate.sample_type.in_([processsing_enum, ProtocolSampleType.ALL])).all()

    setattr(
        StaticForm,
        "processing_template",
        SelectField("Processing Template (Aliquot)", coerce=int, choices=[(x.id, "LIMBPRO-%i: %s" % (x.id, x.name)) for x in processing_templates])
    )

    return StaticForm(), len(processing_templates)