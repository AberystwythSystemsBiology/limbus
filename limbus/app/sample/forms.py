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
from wtforms.validators import DataRequired

from .enums import *
from ..document.models import Document, DocumentType
from ..auth.models import User
from ..misc.enums import UnitsOfMeasurement
from .models import SampleDocumentAssociation
from ..patientconsentform.models import ConsentFormTemplate, ConsentFormTemplateQuestion

from .. import db

import inflect

p = inflect.engine()


class SampleCreationForm(FlaskForm):

    collection_date = DateField(validators=[DataRequired()])

    sample_status = SelectField(
        "Sample Status", validators=[DataRequired()], choices=SampleStatus.choices()
    )

    disposal_date = DateField(validators=[DataRequired()])
    disposal_instruction = SelectField(
        "Disposal Instructions",
        validators=[DataRequired()],
        choices=DisposalInstruction.choices(),
    )


class SampleAttributeCreationForm(FlaskForm):
    term = StringField("Attribute Term", validators=[DataRequired()])
    term_type = SelectField(
        "Attribute Type",
        validators=[DataRequired()],
        choices=[(x.name, x.value) for x in SampleAttributeTypes],
    )
    required = BooleanField("Required")
    submit = SubmitField("Submit")


class SampleAttributionCreationFormText(FlaskForm):
    max_length = StringField(
        "Maximum Length",
        validators=[DataRequired()],
        description="The maximum length of characters that a user can enter",
        default="1024",
    )
    submit = SubmitField("Submit")


class SampleAttributeCreationFormNumeric(FlaskForm):
    type = SelectField(
        "Unit of Measurement",
        validators=[DataRequired()],
        choices=[(x.name, x.value) for x in UnitsOfMeasurement],
    )
    submit = SubmitField("Submit")


def DynamicAttributeSelectForm(query, attr):
    class StaticForm(FlaskForm):
        pass

    for attribute in query:

        bool = BooleanField(getattr(attribute, attr))

        setattr(bool, "_required", attribute.required)

        # Sett additional attrs.
        setattr(StaticForm, p.number_to_words(attribute.id), bool)

    setattr(StaticForm, "submit", SubmitField())
    return StaticForm()


def PatientConsentFormSelectForm():
    class StaticForm(FlaskForm):
        pass

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
        pass

    length = 0

    choices = []

    for t in templates:
        id = t.id
        length += 1
        choice = " LIMBPRO-%s: %s" % (id, t.name)
        choices.append([str(id), choice])

    setattr(
        StaticForm,
        "form_select",
        SelectField(
            "Processing Protocol Template",
            validators=[DataRequired()],
            choices=choices,
        ),
    )

    setattr(
        StaticForm,
        "processing_date",
        DateField("Processing Date", validators=[DataRequired()]),
    )

    setattr(
        StaticForm,
        "processing_time",
        TimeField("Processing Time", validators=[DataRequired()]),
    )

    setattr(StaticForm, "submit", SubmitField())

    return StaticForm(), length


def PatientConsentQuestionnaire(questions) -> FlaskForm:
    class StaticForm(FlaskForm):
        pass

    for question in questions:
        setattr(
            StaticForm, p.number_to_words(question.id), BooleanField(question.question)
        )

    # Inject submit

    setattr(StaticForm, "submit", SubmitField("Submit"))
    return StaticForm()


class SampleTypeSelectForm(FlaskForm):
    sample_type = SelectField(
        "Sample Type", choices=SampleType.choices()
    )

    fluid_sample_type = SelectField(
        "Fluid Sample Type", choices=FluidSampleType.choices()
    )
    molecular_sample_type = SelectField(
        "Molecular Sample Type", choices=MolecularSampleType.choices()
    )
    cell_sample_type = SelectField(
        "Cell Sample Type", choices=CellSampleType.choices()
    )

    # This needs to have some jQuery fiddling to make it work as intented
    quantity = StringField(
        "Quantity"
    )


    submit = SubmitField("Submit")


def SampleAliquotingForm(sample_type, default_type) -> FlaskForm:
    if sample_type == "FLU":
        enums = FluidSampleType
    elif sample_type == "CEL":
        enums = CellSampleType
    else:
        enums = MolecularSampleType

    class StaticForm(FlaskForm):
        count = IntegerField("Aliquot Count")
        size = StringField("Sample per Aliquot")
        aliquot_date = DateField("Aliquot Date", validators=[DataRequired()])
        aliquot_time = TimeField("Aliquot Time", validators=[DataRequired()])
        cell_viability = IntegerField("Cell Viability %")
        lock_parent = BooleanField("Lock Parent?")

        submit = SubmitField("Submit")

    setattr(StaticForm, "sample_type", SelectField("Sample Type", choices=SampleType.choices()))

    return StaticForm()