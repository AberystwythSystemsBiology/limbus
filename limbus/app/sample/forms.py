from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, DateField, BooleanField
from wtforms.validators import DataRequired

from .enums import SampleAttributeTypes, DisposalInstruction, SampleType, SampleStatus
from ..document.models import Document, DocumentType
from ..auth.models import User
from ..misc.enums import UnitsOfMeasurement
from .models import SampleDocumentAssociation

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
        default="1024"
    )
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
        setattr(StaticForm, p.number_to_words(attribute.id),
                BooleanField(getattr(attribute, attr)))

    setattr(StaticForm, "submit", SubmitField())
    return StaticForm()


def PatientConsentFormSelectForm():
    class StaticForm(FlaskForm):
        pass

    length = 0

    patient_consent_forms = db.session.query(
        Document, User).filter(Document.uploader == User.id).filter(
            Document.type == DocumentType.PATIE).all()

    choices = []

    for cf, user in patient_consent_forms:
        id = cf.id

        length += 1

        choice = " LIMBDOC-%s: %s - Uploaded by %s on %s" % (
            cf.id, cf.name, user.email, cf.upload_date.strftime('%Y-%m-%d'))

        choices.append([str(id), choice])

    setattr(
        StaticForm, "form_select",
        SelectField("Patient Consent Form",
                    validators=[DataRequired()],
                    choices=choices))

    setattr(StaticForm, "submit", SubmitField())

    return StaticForm(), length
