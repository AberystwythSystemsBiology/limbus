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
from flask import url_for

from wtforms import (
    StringField,
    SelectField,
    SubmitField,
    ValidationError,
    DateField,
    BooleanField,
    IntegerField,
    FloatField,
    TextAreaField,
)

from wtforms.validators import DataRequired, Length, Optional
from ..validators import validate_against_text

from ..misc import get_internal_api_header

from .enums import AttributeType, AttributeElementType, AttributeTextSettingType

from .models import Attribute, AttributeOption, AttributeTextSetting

import requests

# Pronto stuff here.
import pronto
import urllib

try:

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
except Exception:
    units, prefixs = [], []


class EnumFromOntology:
    def __init__(self, ontology_list):
        self.ontology_list = ontology_list

    def choices(self):
        return [(term.id, term.name) for term in self.ontology_list]


class DoidValidatingSelectField(SelectField):
    def pre_validate(self, form):
        print("self data", self.data)
        iri_repsonse = requests.get(
            url_for("api.doid_validate_by_iri", _external=True),
            headers=get_internal_api_header(),
            json={"iri": self.data},
        )

        if iri_repsonse.status_code != 200:
            if self.data is not None:
                raise ValidationError("%s is not a valid DOID iri" % (self.data))


# def AttributeEditForm(data={}, subclasses=[("", "None")]):
#     class StaticForm(FlaskForm):
#     #class AttributeEditForm(FlaskForm):
#         term = StringField(
#             "Attribute Term",
#             validators=[DataRequired()],
#             description="A word or phrase used to describe a thing or to express a concept.",
#         )
#         accession = StringField("Ontology Accession", render_kw={"disabled": ""})
#         ref = StringField("Ontology Reference", render_kw={"disabled": ""})
#         description = TextAreaField(
#             "Attribute Description",
#             description="An optional description of the custom attribute.",
#         )
#
#         submit = SubmitField("Submit")
#
#     return StaticForm(data=data)


def AttributeEditForm(data={}, subclasses=[("", "None")]):

    if "accession" in data:
        onto_terms = [(data["accession"], data["accession"])]
    else:
        onto_terms = []

    onto_terms.append(["", "None"])

    class StaticForm(FlaskForm):
        term = StringField(
            "Attribute Term",
            validators=[DataRequired()],
            description="A word or phrase used to describe a thing or to express a concept.",
        )
        # accession = StringField("Ontology Accession", render_kw={"disabled": ""})
        # ref = StringField("Ontology Reference", render_kw={"disabled": ""})
        subclass = SelectField("Subclasses of DOID", choices=subclasses, default="")

        # accession = StringField("Ontology Accession")
        accession = DoidValidatingSelectField(
            "DOID term", choices=onto_terms, validators=[Optional()]
        )
        ref = StringField("Ontology References")

        description = TextAreaField(
            "Attribute Description",
            description="An optional description of the custom attribute.",
        )
        type = StringField(
            "Attribute Type",
            description="The 'type' of data this attribute should represent.",
            render_kw={"readonly": True},
        )

        element_type = SelectField(
            "Element Type",
            choices=AttributeElementType.choices(),
            description="If required, you can limit what can use this attribute.",
        )
        submit = SubmitField("Submit")

    return StaticForm(data=data)


def AttributeCreationForm(data={}, subclasses=[("", "None")]):
    class StaticForm(FlaskForm):
        term = StringField(
            "Attribute Term",
            validators=[DataRequired()],
            description="A word or phrase used to describe a thing or to express a concept.",
        )
        # accession = StringField("Ontology Accession", render_kw={"disabled": ""})
        # ref = StringField("Ontology Reference", render_kw={"disabled": ""})
        subclass = SelectField("Subclasses of DOID", choices=subclasses, default="")

        # accession = StringField("Ontology Accession")
        accession = DoidValidatingSelectField("DOID term", validators=[Optional()])
        ref = StringField("Ontology References")

        description = TextAreaField(
            "Attribute Description",
            description="An optional description of the custom attribute.",
        )
        type = SelectField(
            "Attribute Type",
            choices=AttributeType.choices(),
            description="The 'type' of data this attribute should represent.",
        )
        element_type = SelectField(
            "Element Type",
            choices=AttributeElementType.choices(),
            description="If required, you can limit what can use this attribute.",
        )
        submit = SubmitField("Submit")

    return StaticForm(data=data)


class AttributeTextSetting(FlaskForm):
    max_length = IntegerField(
        "Max Length",
        validators=[DataRequired()],
        description="The maximum number of characters allowed in the attribute.",
    )
    type = SelectField(
        "Text Entry Type",
        choices=AttributeTextSettingType.choices(),
        description="The type of user input expected. Tip: If you expect a large input, use the Text Area option.",
    )

    submit = SubmitField("Submit")


class CustomTextAttributeCreationForm(FlaskForm):
    max_length = IntegerField("Max Length", validators=[DataRequired()])
    submit = SubmitField("Submit")


class CustomNumericAttributionCreationForm(FlaskForm):
    requires_measurement = BooleanField("Measurement?")
    requires_symbol = BooleanField("Symbol?")
    measurement = SelectField("Measurement", choices=EnumFromOntology(units).choices())
    symbol = SelectField("Symbol", choices=EnumFromOntology(prefixs).choices())
    submit = SubmitField("Submit")


def AttributeOptionCreationForm(subclasses=[("", "None")]):
    class StaticForm(FlaskForm):
        # class AttributeOptionCreationForm(FlaskForm, subclasses=[(0, "None")]):
        term = StringField(
            "Option Term",
            validators=[DataRequired()],
            description="A word or phrase used to describe a thing or to express a concept.",
        )

        subclass = SelectField("Subclasses of DOID", choices=subclasses)
        accession = DoidValidatingSelectField("DOID term", validators=[Optional()])

        # accession = StringField("Ontology Accession", render_kw={"disabled": ""})
        ref = StringField("Ontology References")  # , render_kw={"disabled": ""})
        submit = SubmitField("Submit")

    return StaticForm()


def AttributeLockForm(id):
    class StaticForm(FlaskForm):
        submit = SubmitField("Submit")

    setattr(
        StaticForm,
        "name",
        StringField(
            "Please enter LIMBATTR-%s to continue" % (str(id)),
            [DataRequired(), validate_against_text("LIMBATTR-%s" % (str(id)))],
        ),
    )

    return StaticForm()


def CustomAttributeSelectionForm(element) -> FlaskForm:
    class StaticForm(FlaskForm):
        submit = SubmitField("Continue")

    custom_attribute_response = requests.get(
        url_for("api.attribute_query", _external=True),
        headers=get_internal_api_header(),
        json={"element_type": element, "is_locked": False},
    )

    if custom_attribute_response.status_code == 200:
        for attr in custom_attribute_response.json()["content"]:
            setattr(
                StaticForm,
                str(attr["id"]),
                BooleanField(attr["term"], render_kw={"_type": attr["type"]}),
            )

    return StaticForm()


def CustomAttributeGeneratedForm(attribute_ids: []) -> FlaskForm:
    class StaticForm(FlaskForm):
        submit = SubmitField("Submit")

    attributes = []

    for attr_id in attribute_ids:
        attr_response = requests.get(
            url_for("api.attribute_view_attribute", id=attr_id, _external=True),
            headers=get_internal_api_header(),
        )

        if attr_response.status_code == 200:
            attributes.append(attr_response.json()["content"])

    for attr in attributes:
        print("attr: ", attr)
        if attr["type"] == "Text":
            if attr["text_setting"]["type"] == "SF":
                element = StringField(
                    attr["term"],
                    description=attr["description"],
                    validators=[
                        DataRequired(),
                        Length(max=attr["text_setting"]["max_length"]),
                    ],
                    render_kw={"_custom_val": True},
                )

            else:
                element = TextAreaField(
                    attr["term"],
                    description=attr["description"],
                    validators=[
                        DataRequired(),
                        Length(max=attr["text_setting"]["max_length"]),
                    ],
                    render_kw={"_custom_val": True},
                )
        elif attr["type"] == "Option":
            choices = []

            for choice in attr["options"]:
                choices.append([int(choice["id"]), choice["term"]])

            element = SelectField(
                attr["term"],
                description=attr["description"],
                choices=choices,
                coerce=int,
                render_kw={"_custom_val": True},
            )
        elif attr["type"] == "Numeric":
            element = FloatField(attr["term"], render_kw={"_custom_val": True})
            ontology

        element.render_kw = {"_custom_val": True}

        setattr(StaticForm, str(attr["id"]), element)

    return StaticForm()


"""

def CustomAttributeGeneratedForm(form, attribute_ids: [] = []) -> FlaskForm:
    class StaticForm(FlaskForm):
        pass

    for id, element in form.elements.items():
        setattr(StaticForm, id, element)

    attrs = (
        db.session.query(CustomAttributes)
        .filter(CustomAttributes.id.in_(attribute_ids))
        .all()
    )

    for attr in attrs:
        if attr.type == CustomAttributeTypes.NUMERIC:
            field = IntegerField(attr.term, render_kw={"_custom_val": True})
        elif attr.type == CustomAttributeTypes.TEXT:
            text_settings = (
                db.session.query(CustomAttributeTextSetting)
                .filter(CustomAttributeTextSetting.custom_attribute_id == attr.id)
                .first_or_404()
            )
            field = StringField(
                attr.term,
                render_kw={"_custom_val": True},
                validators=[Length(max=text_settings.max_length)],
            )
        else:
            options = (
                db.session.query(CustomAttributeOption)
                .filter(CustomAttributeOption.custom_attribute_id == attr.id)
                .all()
            )
            choices = [(x.id, x.term) for x in options]
            field = SelectField(
                attr.term, choices=choices, coerce=int, render_kw={"_custom_val": True}
            )

        if attr.required:
            field.validators.append(DataRequired())

        setattr(StaticForm, str(attr.id), field)

    return StaticForm()
"""
