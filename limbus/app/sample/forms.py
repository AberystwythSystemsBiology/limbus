from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, DateField, BooleanField
from wtforms.validators import DataRequired

from .enums import SampleAttributeTypes, DisposalInstruction, SampleType, SampleStatus

import inflect

p = inflect.engine()

class SampleCreationForm(FlaskForm):
    sample_type = SelectField("Sample Type", validators=[DataRequired()],
                              choices=SampleType.choices())

    collection_date = DateField(validators=[DataRequired()])


    sample_status = SelectField("Sample Status", validators=[DataRequired()],
                                choices=SampleStatus.choices())


    batch_number = StringField("Batch Number")


    disposal_date = DateField(validators=[DataRequired()])
    disposal_instruction = SelectField("Disposal Instructions", validators=[DataRequired()],
                                       choices=DisposalInstruction.choices())

class SampleAttributeCreationForm(FlaskForm):
    term = StringField("Attribute Term", validators=[DataRequired()])
    term_type = SelectField("Attribute Type", validators=[DataRequired()], choices=[(x.name, x.value) for x in SampleAttributeTypes])
    required = BooleanField("Required")
    submit = SubmitField("Submit")

class SampleAttributionCreationFormText(FlaskForm):
    max_length = StringField("Maximum Length", validators=[DataRequired()])
    submit = SubmitField("Submit")

def DynamicAttributeSelectForm(query, attr):
    class StaticForm(FlaskForm):
        pass

    for attribute in query:
        setattr(StaticForm, p.number_to_words(attribute.id), BooleanField(getattr(attribute, attr)))

    setattr(StaticForm, "submit", SubmitField())
    return StaticForm()
