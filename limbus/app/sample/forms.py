from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, DateField, BooleanField
from wtforms.validators import DataRequired

from .enums import SampleAttributeTypes, DisposalInstruction, SampleType, SampleStatus
from ..document.models import Document, DocumentType
from ..auth.models import User
from ..misc.enums import UnitsOfMeasurement
from .models import SampleDocumentAssociation
from ..patientconsentform.models import ConsentFormTemplate, ConsentFormTemplateQuestion

from .. import db

import inflect

p = inflect.engine()


class SampleCreationForm(FlaskForm):
    sample_type = SelectField("Sample Type",
                              validators=[DataRequired()],
                              choices=SampleType.choices())

    collection_date = DateField(validators=[DataRequired()])

    sample_status = SelectField("Sample Status",
                                validators=[DataRequired()],
                                choices=SampleStatus.choices())

    batch_number = StringField("Batch Number")

    disposal_date = DateField(validators=[DataRequired()])
    disposal_instruction = SelectField("Disposal Instructions",
                                       validators=[DataRequired()],
                                       choices=DisposalInstruction.choices())


class SampleAttributeCreationForm(FlaskForm):
    term = StringField("Attribute Term", validators=[DataRequired()])
    term_type = SelectField("Attribute Type",
                            validators=[DataRequired()],
                            choices=[(x.name, x.value)
                                     for x in SampleAttributeTypes])
    required = BooleanField("Required")
    submit = SubmitField("Submit")


class SampleAttributionCreationFormText(FlaskForm):
    max_length = StringField(
        "Maximum Length",
        validators=[DataRequired()],
        description="The maximum length of characters that a user can enter",
        default="1024")
    submit = SubmitField("Submit")


class SampleAttributeCreationFormNumeric(FlaskForm):
    type = SelectField("Unit of Measurement",
                       validators=[DataRequired()],
                       choices=[(x.name, x.value) for x in UnitsOfMeasurement])
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

    patient_consent_forms = db.session.query(
        ConsentFormTemplate, User).filter(ConsentFormTemplate.uploader == User.id).all()

    choices = []

    for cf, user in patient_consent_forms:
        id = cf.id
        length += 1
        choice = " LIMBPCF-%s: %s" % (
            cf.id, cf.name)
        choices.append([str(id), choice])

    setattr(
        StaticForm, "form_select",
        SelectField("Patient Consent Form Template",
                    validators=[DataRequired()],
                    choices=choices))

    setattr(StaticForm, "submit", SubmitField())

    return StaticForm(), length
