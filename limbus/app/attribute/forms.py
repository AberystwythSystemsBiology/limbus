from flask_wtf import FlaskForm
from wtforms import (
    SelectField,
    StringField,
    SubmitField,
    DateField,
    BooleanField,
    IntegerField,
)

from wtforms.validators import DataRequired

from .enums import *

from .. import db
from .models import CustomAttributes


# Pronto stuff here.
import pronto

# Loading UO into memory upon creation of flask instance.
uo = pronto.Ontology.from_obo_library("uo.obo")

def create_uo_params():
    def _get_leafs(node):
        leafs = []
        def _traverse(n):
            n = [x for x in n.subclasses()]
            if len(n[1:]) > 1:
                for _n in n[1:]:
                    _traverse(_n)
            elif len(n) == 1:
                leafs.extend(n)
            else:
                pass

        _traverse(node)
        return list(set(leafs))


    # Loading UO into memory upon creation of flask instance.
    uo_ontology = pronto.Ontology.from_obo_library("uo.obo")
    units = _get_leafs(uo_ontology["UO:0000000"])
    prefixs = _get_leafs(uo_ontology["UO:0000046"])

    return units, prefixs

units, prefixs = create_uo_params()


class EnumFromOntology:
    def __init__(self, ontology_list):
        self.ontology_list = ontology_list

    def choices(self):
        return [(term.id, term.name) for term in self.ontology_list]

class CustomAttributeCreationForm(FlaskForm):
    term = StringField("Attribute Term", validators=[DataRequired()])
    description = StringField("Attribute Description")
    accession = StringField("Ontology Accession")
    ref = StringField("Ontology Reference")
    type = SelectField("Attribute Type", choices=CustomAttributeTypes.choices())
    element = SelectField("Element", choices=CustomAttributeElementTypes.choices())
    required = BooleanField("Required")
    submit = SubmitField("Submit")

class CustomTextAttributeCreationForm(FlaskForm):
    max_length = IntegerField("Max Length", validators=[DataRequired()])
    submit = SubmitField("Submit")

class CustomNumericAttributionCreationForm(FlaskForm):
    requires_measurement = BooleanField("Measurement?")
    requires_prefix = BooleanField("Prefix?")
    measurement = SelectField("Measurement", choices=EnumFromOntology(units).choices())
    prefix = SelectField("Prefix", choices=EnumFromOntology(prefixs).choices())
    submit = SubmitField("Submit")


def CustomAttributeSelectForm(element: CustomAttributeElementTypes = CustomAttributeElementTypes.ALL) -> FlaskForm:
    class StaticForm(FlaskForm):
        submit = SubmitField("Submit")

    attrs = db.session.query(CustomAttributes).filter(CustomAttributes.element.in_([element, CustomAttributeElementTypes.ALL])).all()

    for attr in attrs:
        bf = BooleanField(
            attr.term,
            render_kw={
                "required": attr.required,
                "_type" : attr.type.value
            })

        setattr(StaticForm, str(attr.id), bf)

    return StaticForm()

