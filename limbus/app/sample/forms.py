from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, DateField
from wtforms.validators import DataRequired

from .enums import SampleAttributeTypes, DisposalInstruction, SampleType

class SampleCreationForm(FlaskForm):
    sample_type = SelectField("Sample Type", validators=[DataRequired()],
                              choices=SampleType.choices())
    disposal_instruction = SelectField("Disposal Instructions", validators=[DataRequired()],
                                       choices=DisposalInstruction.choices())
    collection_date = DateField()
    submit = SubmitField("Submit")


class SampleAttributeCreationForm(FlaskForm):
    term = StringField("Attribute Term", validators=[DataRequired()])
    term_type = SelectField("Attribute Type", validators=[DataRequired()], choices=[(x.name, x.value) for x in SampleAttributeTypes])
    submit = SubmitField("Submit")

class DynamicAttributeSelectForm(FlaskForm):
        submit = SubmitField("Submit")    
